# Task #4 Evaluation Findings — Compatibility Model

Compiled 2026-08-10/11 from `notebooks/03_football_feature_engineering.ipynb` and `notebooks/04_player_manager_compatibility.ipynb`. This document went through three drafts as successive bugs were found and fixed; only §5-6 reflect the final, corrected pipeline. The earlier drafts are preserved in spirit below (§1-4) because the debugging path itself is part of the academic record this project needs (methodological honesty, brief §32/§38) — but **only §5 onward should be cited as the project's actual findings.**

## 1. What was built

- Cosine similarity between each player-season's 7-dimension profile and each of the 3 managers' centroid profiles (brief §23: a similarity score, explicitly not a probability).
- Football-language explanations decomposed from actual per-dimension contribution numbers (brief §24-26).
- A club-identity-bias check using De Zerbi's four in-scope clubs — the only manager with more than one in-scope club, so the only direct test available with current data (Guardiola/Klopp are single-club within the open-data window, decision_log.md D-005).

## 2. First finding (v1, later shown to be a data bug, not a real result)

The first working version showed a dramatic club-bias failure: Sassuolo and Benevento centroids at cosine similarity ≈ **-0.6 to -0.66** with every other club, while Brighton/Marseille/Liverpool/Man City all clustered at **+0.95 to +0.998**. This looked, at first, like a clean demonstration of squad-strength dominating the signal.

## 3. Root cause was a data-integrity bug, not a real finding

Investigating *why* the split was so clean (rather than accepting it) surfaced two compounding bugs:

1. **A `fillna(0)` in the feature-construction code** (`compute_concept_terms` in `src/football_features.py`) was converting genuinely-missing raw columns into fake zeros before computing per-90 rates and ratios — so "no data available" was silently reported as "did zero of this action," which then averaged into manager/club profiles as if it were real, extreme, information.
2. **A previously-undetected data-coverage gap**: FBref's match-level `passing`, `passing_types`, `possession` and `keeper` blocks are **not populated for Serie A/Ligue 1 before the 2023/24 season** (0% non-null for every relevant column, confirmed by direct audit — see `outputs/audit/data_availability_matrix.md` §5, `decision_log.md` D-006). Sassuolo (all 3 in-scope seasons) and Benevento sit entirely inside this gap. The `summary` block (needed for shot/chance-creation detail) turned out to be missing for **every** club before 2025, not just Sassuolo/Benevento.

Both bugs were fixed: no `fillna(0)` anywhere in the feature pipeline (missing data stays `NaN` and propagates honestly); every aggregation step (`build_player_profiles`, `build_manager_profiles`, `build_club_within_manager_profiles`, the population-baseline pooling, and the compatibility/similarity computation) was rewritten to skip `NaN` per-column with re-normalised weights, rather than silently substituting zero; `chance_creation` and `box_presence` were redefined to drop the terms that depended on the entirely-unavailable `summary` block; and every compatibility/similarity comparison now records `n_dims_used` and a `low_confidence` flag so a thin 1-2-dimension comparison is visible rather than hidden.

## 4. Intermediate finding (partially fixed, still had a pooling bug)

A second pooling bug in `build_population_baseline` (non-NaN-aware `np.average` letting a single zero-coverage league poison a pooled statistic to NaN for *everyone*, not just the affected league) was found and fixed after `TD7_box_presence` came out `NaN` for all three managers simultaneously — including Guardiola and Klopp, whose data was actually fine. This is documented in `decision_log.md` D-006 alongside the main fix, since it's the same class of error (a NaN-unaware aggregation) surfacing in a different function.

## 5. Final, corrected results

**Manager profiles (7 tactical dimensions, minutes-weighted, NaN-aware):**

| | TD1 buildup | TD3 progr. passing | TD4 progr. carrying | TD6 chance creation | TD7 box presence | TD9 pressing | TD11 ind. defending |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Jürgen Klopp** | 0.197 | 0.147 | 0.012 | 0.014 | 0.145 | -0.021 | -0.156 |
| **Pep Guardiola** | 0.304 | 0.196 | 0.046 | 0.013 | 0.139 | -0.060 | -0.208 |
| **Roberto De Zerbi** | 0.193 | 0.122 | -0.030 | -0.006 | 0.052 | -0.076 | -0.044 |

(De Zerbi's TD1/TD3/TD4/TD6/TD7 values are now built **only** from Brighton and Marseille — Sassuolo and Benevento correctly contribute `NaN`, i.e. nothing, to these five dimensions, per §3-4 above.)

**Best-fit match rate, restricted to comparisons with ≥4 of 7 dimensions available (77.6% of all player-season × manager comparisons meet this bar):**

> **32.8%** of player-seasons have their single best-fit manager equal to the manager they actually played under (n=470). **Chance baseline for 3 classes is ~33%.**

| actual → scored as | Klopp | Guardiola | De Zerbi |
|---|---:|---:|---:|
| Klopp | 61 | 36 | 90 |
| Guardiola | 46 | 41 | 81 |
| De Zerbi | 39 | 24 | 52 |

**Club-identity-bias check, restricted to well-covered (≥4-dimension) pairs:**

- De Zerbi's own two well-covered clubs (Brighton, Marseille) resemble each other at **0.583**.
- Those same two clubs resemble Klopp's/Guardiola's clubs at **0.706** on average.
- **De Zerbi's clubs do not resemble each other more than they resemble the other two managers, even after every data-integrity fix.**

## 6. Honest interpretation

This is a real, sobering result, not a residual bug — it survived a thorough root-causing pass that fixed two genuine, non-trivial data-integrity errors along the way, and the fixes moved the numbers substantially (§2 vs §5) without producing the hoped-for signal. Three things are true simultaneously, and the report should say all three:

1. **The pipeline is now trustworthy for what it measures.** Every step from raw FBref columns to manager/player profiles to compatibility scores has been checked for NaN-propagation correctness, and the two bugs that were found were found *because* an implausibly clean result triggered suspicion, root-caused, and fixed rather than reported — exactly the methodological discipline brief §32/§38 asks for.
2. **A 7-dimension, per-90/ratio, position-normalised feature set built from match-level box-score-style statistics does not, on this evidence, separate these three managers' philosophies from squad/league context better than chance**, at least not with the simple cosine-similarity-to-centroid method used here. This is a legitimate, reportable academic finding in its own right (a documented case where a plausible knowledge-informed approach did not clear the bar it needs to clear to be useful) — not a failure to hide.
3. **The specific mechanism is diagnosable, not mysterious**: Liverpool, Man City and Brighton (three well-resourced clubs, three different managers) cluster at 0.97-0.998 similarity with each other regardless of manager, while Marseille (De Zerbi, but a less dominant squad in a different league) sits apart at 0.4-0.6 from all of them, including from Brighton (De Zerbi's *other* club). This is much closer to a squad-competitiveness/possession-share signal than a managerial-philosophy signal, even after switching from raw per-90 volume to within-team share/ratio metrics (which measurably helped in the earlier iteration but evidently did not go far enough).

## 6b. Dimension-level permutation importance (explainability polish)

SHAP requires a trained predictive model; the compatibility score here is a similarity computation, not a fitted classifier, so SHAP does not apply directly. The substitute used (`notebooks/04_player_manager_compatibility.ipynb` §6): shuffle one dimension at a time across all player-seasons and measure the resulting drop in the best-fit match rate (baseline 32.8%, n=470).

| Dimension | Importance (match-rate drop when shuffled) |
|---|---:|
| **TD9 pressing intensity** | **+2.55 pp** |
| TD1 buildup directness | +0.71 pp |
| TD6 chance creation | +0.71 pp |
| TD4 progression carrying | +0.14 pp |
| TD3 progression passing | -0.28 pp |
| TD7 box presence | -1.49 pp |
| TD11 individual defending | -1.91 pp |

**Pressing intensity is the only dimension carrying real, positive discriminating signal** — consistent with H-P1 (`manager_philosophy_hypotheses.md` §4.2), which specifically predicted this dimension would be the easiest to separate Klopp on. Box presence and individual defending are actively *hurting* accuracy (shuffling them improves the match rate) — likely residual noise from their reduced/partial feature definitions (§3-4 above) rather than a real anti-signal, and should be reported as unreliable rather than as a negative finding in their own right. This is a genuine, reportable positive result nested inside an overall negative one: not "nothing works," but "one specific, hypothesis-predicted dimension works; the rest currently do not."

## 6c. Update after season-level data integration (`notebooks/05_season_level_integration.ipynb`, 2026-08-11)

A follow-up discovery: FBref's **season-level** aggregated tables (as opposed to the match-level tables used above) have full 2017/18-2022/23 coverage across all five big-5 leagues, including Serie A/Ligue 1 — closing most of the Sassuolo/Benevento gap for Sassuolo specifically (a SAFE, whole-season De Zerbi tenure, unlike Benevento's mid-season split, which season-level data cannot resolve either). This was used to recover real `progressive_passing`/`progressive_carrying`/`possession_retention`/`chance_creation`/`box_presence` data for Sassuolo's 337 player-seasons, previously entirely `NaN`.

**Result: a modest, real improvement, not a reversal.**
- Best-fit match rate: **37.8%** (n=558), up from 32.8% (n=470) — better than chance, but not by a wide margin.
- De Zerbi's own club-to-club similarity (now across 4 well-covered clubs instead of 2): **0.659**; De Zerbi's clubs vs. the other two managers: **0.765**. His clubs still do not resemble each other more than they resemble Klopp's/Guardiola's — the core finding stands even with substantially richer data.

This corroborates the §6 diagnosis: the limiting factor is the **feature design** (box-score-derived per-90/ratio statistics correlating with squad/league strength), not primarily a data-coverage artefact. Filling the coverage gap helped a little (as it should — more real signal, less missing data) but did not change the fundamental conclusion.

## 7a. Update after analyst-driven feature improvements (2026-08-11)

Asked to review the whole project as a football analyst rather than an engineer, three concrete critiques were identified and implemented (see `decision_log.md` D-007 for full detail):

1. **Role-based position groups.** Replaced the 4 coarse buckets (GK/Defender/Midfielder/Forward) with 8 role-based groups (Centre-back, Full-back/Wing-back, Defensive Midfielder, Central Midfielder, Attacking Midfielder, Winger/Second Striker, Striker, Goalkeeper), using FBref's specific match-level position tags (CB/LB/RB/DM/CM/AM/LM/RM/LW/RW/FW/GK) directly, with a touches-by-third zone heuristic as a fallback for season-level data's coarser tags. A central midfielder, a defensive pivot and an attacking #10 have very different baselines on every dimension; z-scoring them together was role noise sitting on top of any managerial signal.
2. **Possession-adjusted pressing intensity** (closes OD-5, open since the Phase 0 proposal). Raw defensive-action counts are scaled by `league_avg_opponent_possession / this_team's_opponent_possession`, using real team possession-share data (`data/raw/fbref_season/team_possession.parquet`) — a team that dominates the ball faces less opponent-in-possession time and so racks up fewer raw defensive actions for the same underlying pressing intent; this corrects for that.
3. **Goalkeeper distribution features.** A new `goalkeeper_distribution` concept (average pass length, % of passes launched/long, launch completion %) feeding `TD1_buildup_directness` — using `keeper`/`keepers_adv` block data that was already collected but never used, despite the project's own qualitative research (`manager_philosophy_hypotheses.md`) naming the goalkeeper-as-auxiliary-defender mechanism as one of the clearest discriminators for Guardiola and De Zerbi specifically.

**Result: a real, material improvement — not a marginal one.**

| Metric | Pre-improvement | Post-improvement |
|---|---:|---:|
| Best-fit match rate | 37.8% (n=558) | **42.1%** (n=561) |
| Pressing intensity permutation importance | +2.55pp | **+7.49pp** (still the single strongest dimension, by a wide margin) |
| Buildup directness / progression passing importance | +0.71pp each | **+3.21pp each** (now clearly real signal) |
| Progression carrying importance | +0.14pp | **+2.67pp** (now clearly real signal) |
| Individual defending importance | -1.91pp (noise) | **+1.78pp** (now real signal, not noise) |
| Box presence / chance creation importance | -1.49pp / +0.71pp | **-0.36pp / -0.71pp** (both remain slightly negative — noise, not signal) |
| De Zerbi within-club similarity vs. between-manager similarity | 0.659 vs 0.765 (gap 0.106) | **0.799 vs 0.816** (gap 0.017 — nearly closed) |

(Verified 2026-08-26 by an independent, from-scratch recomputation against the saved `player_profiles.parquet`/`manager_profiles.parquet`, exactly reproducing `outputs/tables/dimension_permutation_importance.csv` — see D-009 in `decision_log.md`. This corrects an earlier, incorrect version of this table, which had understated pressing intensity's importance and incorrectly reported box presence as having flipped to a positive contributor.)

The club-bias gap did not fully close, but narrowed by roughly 6x (from a 0.106 similarity gap to 0.017). Best-fit accuracy is now clearly and meaningfully above the ~33% chance baseline, not just marginally so. Pressing intensity's dominance grew even further than first reported — nearly tripling rather than merely doubling — and three further dimensions (buildup directness, progression passing, progression carrying) turned out to carry real positive signal as well, a broader positive result than originally described. Box presence remains a mild net-negative, meaning the more detailed positional grouping did not rescue it the way it rescued individual defending. This is exactly the kind of improvement the diagnosis in §6 predicted: the confound was never really about a single missing feature, but the analyst-identified fixes (role precision, possession-adjustment, an unused-but-relevant data source) all directly targeted mechanisms the qualitative research had already flagged as real, and most of them moved the needle in the right direction simultaneously.

**Updated interpretation.** The project's central finding shifts from "this feature set cannot discriminate the three managers" to "a knowledge-informed feature set, once refined with football-analytical judgement (not just more data), discriminates the three managers meaningfully better than chance, with pressing intensity as the strongest and most theoretically-grounded signal — but a residual squad/league-strength confound is still present and not fully resolved." This is a more optimistic, but still honest, conclusion than the original.

## 7. Recommended paths forward (not yet implemented — a decision point, not a default)

- **(a) Accept and report as a limitation-rich finding.** Write up §5-6 above as the core Evaluation-phase result: state the hypotheses, state that the current feature set cannot discriminate them, and discuss why (squad/league-strength confound, thin multi-club coverage for two of three managers, box-score-only data with no tracking/positional detail). This is a legitimate, defensible academic conclusion and requires no further modelling work — it shifts effort toward writing.
- **(b) Attempt a further methodological fix before writing up.** The most promising untried lever is an explicit team-strength control: rather than z-scoring a player against the league-wide position baseline only, additionally residualise against the player's own team's season-average on each dimension (i.e. model "how this player differs from his own teammates," a within-team contrast, alongside or instead of the current between-league contrast). This directly targets the mechanism diagnosed in §6.3 and is a bounded, well-scoped piece of further work — but it is genuinely new modelling, not a bug fix, and would need its own validation pass.
- **(c) Narrow the claim.** Report the pressing-intensity and individual-defending dimensions (the two least affected by the Serie A/Ligue 1 coverage gap and the most conceptually distinct from squad strength) as the project's primary discriminating evidence, and explicitly scope down the build-up/progression dimensions to a qualitative, literature-and-research-supported discussion (`manager_philosophy_hypotheses.md`) rather than a quantitative claim.

This document does not choose between (a)/(b)/(c) — that is a scope decision for the project owner given the two-week timeline, not something to decide unilaterally mid-pipeline.

## 7b. Statistical significance of the 42.1% best-fit rate (`notebooks/04_player_manager_compatibility.ipynb` §2b, 2026-08-11)

The 42.1% figure (§7a) is a single point estimate over n=561 player-seasons. Two checks were added to quantify how much confidence that single number can actually support, both computed from the already-saved `player_manager_compatibility.parquet`, with no new data or model changes:

- **Bootstrap 95% confidence interval** (5000 resamples with replacement): **[37.8%, 46.2%]**, median 42.1%, standard error 0.021. The interval sits entirely above the naive 33% baseline, but it is wide — nearly 8.5 percentage points end to end — so the exact point estimate (42.1%) should be read as "somewhere in the high 30s to mid 40s," not as a precise figure.
- **Permutation test** (5000 shuffles of the true `actual_manager` label against the model's own `scored_against_manager` decisions, 5000 permutations): empirical chance baseline **34.0%** (slightly above the naive 33%, because De Zerbi/Klopp/Guardiola are not represented in exactly equal numbers in the n=561 sample — 203/188/170 respectively), null-distribution standard deviation 0.020, **p = 0.0002**. The observed 42.1% rate exceeded the permuted-null rate in only 1 of 5000 shuffles, so the association between the model's best-fit decision and the true manager is statistically significant at a stringent threshold, not an artefact of this particular sample.

**Reading these two results together.** The permutation test answers "is this better than chance at all," and the answer is a confident yes. The bootstrap interval answers "how precisely is the number known," and the answer is "not very precisely" — a project reporting only the point estimate would risk implying more precision than 561 observations actually support. Both should be reported together rather than either alone.

## 7c. Team formation profiles: explored as an eighth dimension, added descriptively instead (`notebooks/04_player_manager_compatibility.ipynb` §7, 2026-08-11)

The recommended next steps already written into this project (report §6.4, item 6) flagged that `Home_Formation`/`Away_Formation`, collected for every match back in task #2, had been gathered but never analysed. Implementing it surfaced a genuine, worth-recording complication.

**The data-source discovery.** The plan was to add formation as an eighth tactical dimension inside the compatibility score. Re-checking coverage against the live upstream source showed that `worldfootballR_data`'s `fb_advanced_match_stats` GitHub release is a *rolling* asset the maintainer overwrites in place, not a versioned per-season archive: the files currently downloadable from it cover the 2025/26 season, and the 2018-2023 window this project needs is no longer available from that URL at all. The historical formation data was recovered from `data/processed/player_match_manager.parquet`, an intermediate file saved during task #2 that still holds the original snapshot — 10996 rows, 0% missing `Home_Formation`/`Away_Formation`. This is itself a small but genuine addition to this project's catalogue of data-availability findings (`decision_log.md` D-006, D-007): a source being downloadable once does not guarantee it remains downloadable, and any step of the pipeline that only ever re-fetches from a live upstream source, without a cached original snapshot, is exposed to this kind of silent scope loss. Luckily, this project's habit of persisting every intermediate stage to `data/processed/` meant nothing was actually lost.

**Why formation was not folded into the compatibility score.** Formation is only available for the 22 club-seasons inside the manager-attributed match-level sample (Liverpool, Manchester City, Sassuolo, Benevento, Brighton & Hove Albion, Marseille) — never for the wider 11132-player-season population that every other tactical dimension is z-scored against. Standardising a new dimension against a population of 22 would be statistically fragile in a way none of the other 7 dimensions are, so rather than quietly add a weak eighth dimension, the result is reported here as descriptive supporting evidence, kept clearly separate from the numerical compatibility score.

**The result itself** (`outputs/tables/manager_formation_profile.csv`, pooled across each manager's full tenure and every club):

| Manager | Matches | Modal formation | Formation stability | Distinct formations used | Mean back-line size |
|---|---:|---|---:|---:|---:|
| Jürgen Klopp | 266 | 4-3-3 | **86.5%** | 8 | 4.00 |
| Pep Guardiola | 266 | 4-3-3 | 59.8% | 10 | 3.87 |
| Roberto De Zerbi | 237 | 4-2-3-1 | 56.1% | **15** | 3.81 |

Klopp is by a wide margin the most tactically settled of the three, playing his modal 4-3-3 in nearly 9 of every 10 matches — consistent with a manager known for imposing one clear system rather than adapting it constantly. Guardiola experiments considerably more than the "clean, singular possession identity" reputation might suggest, using 10 distinct formations and dropping to a back three often enough to pull his mean back-line size below 4.0. De Zerbi is confirmed as the most structurally fluid of the three by every measure here — the most distinct formations, the lowest stability, and the lowest mean back-line size — which lines up with his description elsewhere in this project as an unconventional, fluid tactician whose signature mechanism operates through shifting shape in possession rather than a fixed structure. This is a genuinely new, independently corroborating piece of evidence for a claim the project was already making on qualitative grounds alone.
