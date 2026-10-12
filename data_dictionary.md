# Data Dictionary

Each entry follows this schema (per brief §44):

| Field | Meaning |
|---|---|
| Variable | Column/feature name as it appears in the pipeline |
| Source | Source A (FBref/Opta match-level) / Source B (StatsBomb) / derived |
| Definition | What it counts/measures, precisely |
| Football meaning | What it indicates tactically |
| Transformation | Per-90, z-score, position-normalised, etc. |
| Limitations | Known caveats (see `outputs/football_knowledge/football_ontology.md` for worked examples) |

## Raw source columns

See `src/data_sources.py` module docstrings and `outputs/audit/data_availability_matrix.md` for the full raw-column inventory per stat block (summary, passing, passing_types, possession, defense, misc, keeper). Not duplicated here to avoid drift between two copies of the same list — this file instead documents **derived/engineered** columns, cross-referencing the raw source column names.

**A note on how this section was produced.** The engineered concepts below are documented exactly as implemented in `src/football_features.py` (`CONCEPTS` and `DIMENSION_WEIGHTS` dicts), which is the ground truth for what was actually built — not `outputs/football_knowledge/football_ontology.md`, which was written earlier in the project (v0.1, before decision D-006) and proposed a richer set of terms than what ended up being computable. Where the code diverges from the original ontology proposal, that divergence is noted explicitly per concept rather than silently reconciled.

**A note on the D-006 data gap (see `decision_log.md`).** During Task #4 it was discovered that the FBref match-level `passing`, `passing_types`, `possession`, and `keeper` stat blocks are **entirely unpopulated (0% coverage) for Serie A (ITA) and Ligue 1 (FRA) for `Season_End_Year` 2018–2023**, becoming available only from 2023/24 onward; the `summary` block is unpopulated for **every** league before 2025. `defense` and `misc` are 100% populated everywhere, always. Because two of De Zerbi's four in-scope tenures — **Sassuolo** (3 full seasons) and **Benevento** (1 season) — fall in Serie A before 2023/24, those two clubs have **no usable data for 6 of the 10 concepts** (`progressive_passing`, `progressive_carrying`, `possession_retention`, `chance_creation`, `box_presence`, and, since D-007, `goalkeeper_distribution` — its `keeper`-block dependency has the same 0% pre-2023/24 Serie A gap) and **partial data for a 7th** (`individual_defending`, whose ratio term needs the missing `possession` block); only `pressing_intensity` (D-007: now possession-adjusted, but still fully computable from the always-populated `defense`/`misc` blocks) and (fully) `individual_defending`'s `asis` term are unaffected for those two clubs. This is called out per-concept below. The code does not `fillna(0)` in this situation — missing blocks propagate as `NaN` through every downstream stage (concept terms → concept scores → player/manager profiles → compatibility), via NaN-aware, weight-renormalising aggregation (`_nan_aware_wmean`), so "no data" is never silently reported as "exactly league average."

## Engineered concepts

**A note on position grouping (D-007).** Every concept score below is z-scored against the population baseline **within the player's position group** (`build_population_baseline` / `build_concept_scores`), so a change to how position groups are defined changes the baseline — and therefore every concept's score, not just one — even though `position_group()` itself is not a "concept." As of D-007, `position_group()` (`src/football_features.py`) produces **8 role-based groups** (`ROLE_GROUPS`: Goalkeeper, Centre-back, Full-back/Wing-back, Defensive Midfielder, Central Midfielder, Attacking Midfielder, Winger/Second Striker, Striker), replacing the earlier 4 coarse GK/Defender/Midfielder/Forward buckets. Match-level FBref data tags a specific role per row (CB/LB/RB/WB/DM/CM/AM/LM/RM/LW/RW/FW/GK), which `_FINE_GRAINED_MAP` maps directly to one of the 8 roles. Season-level data only carries the coarser DF/MF/FW/GK-only tags, which cannot be mapped directly (a first attempt at doing so dumped 8959 of 10996 rows into a single "Central Midfielder" bucket — see decision_log.md D-007); for those coarse tags, `position_group()` falls back to a touches-by-third zone heuristic (`_attacking_third_share`, using `possession__Def/Mid/Att 3rd_Touches`) to distinguish e.g. a stay-at-home centre-back from an advanced wing-back tagged plain "DF". This zone fallback itself degrades to tag-only classification when the `possession` block isn't available for a row (e.g. Benevento match-level rows, D-006).

Concepts are computed by `compute_concept_terms()` in `src/football_features.py`. Each concept is a named list of "terms," where each term is one of:
- `rate` — a raw counting column converted to a per-90 figure (`col * 90 / Min`).
- `padj_rate` — a possession-adjusted per-90 figure: `(col * 90 / Min) * padj_factor`, where `padj_factor` scales up a team's raw rate when its opponents held more of the ball on average (see `pressing_intensity` below and `attach_possession_adjustment()`).
- `ratio` — numerator column / denominator column (a share, e.g. "progressive passes as a fraction of all passes attempted"); denominator of 0 is treated as missing (NaN), not divide-by-zero.
- `asis` — a column that is already a rate or percentage in the raw data, used directly with no further transformation.

A concept's final score is the mean of its terms' **position-group z-scores**, each z-scored against a full big-5-league (ENG/ITA/FRA) population baseline within the same position group (`build_concept_scores` / `build_population_baseline`), not against just the 4–6 clubs in the manager sample — this is deliberate, to avoid conflating managerial philosophy with squad quality. As of D-007, one concept (`goalkeeper_distribution`) has all of its terms inverted (`CONCEPTS["goalkeeper_distribution"]["invert"] == ["t0", "t1", "t2"]`); every other concept's `invert` list remains empty, so no other concept's raw-value polarity is flipped.

---

### progressive_passing

| Field | Content |
|---|---|
| Variable | `progressive_passing` |
| Source | Derived, from Source A (FBref/Opta match-level), stat block `passing` |
| Definition | Mean of four terms: `ratio(passing__PrgP, passing__Att_Total)`, `ratio(passing__Final_Third, passing__Att_Total)`, `ratio(passing__PPA, passing__Att_Total)`, `asis(passing__Cmp_percent_Total)` |
| Football meaning | The tendency to advance possession meaningfully via passing (progressive passes, passes into the final third, passes into the penalty area — each expressed as a *share* of the player's own total pass attempts, not a raw per-90 count) while completion % acts as a quality control on the other three shares |
| Transformation | Ratio terms = numerator/denominator (denominator 0 → NaN); `asis` term used directly; concept score = mean of the four terms' position-group z-scores against the big-5-league population baseline; feeds `TD1_buildup_directness` (weight 0.5, changed from 0.6 under D-007) and `TD3_progression_passing` (weight 1.0) |
| Limitations | Entirely unmeasurable for Sassuolo and Benevento (De Zerbi) — the `passing` block has 0% coverage in Serie A pre-2023/24 (D-006). Differs from the original ontology worked example (`football_ontology.md` §3), which proposed `Prog`/`PrgDist_Total` per-90 rates plus `Final_Third`/`PPA`/`Cmp_percent_Total`; the implemented version uses **share-of-attempts ratios** instead of raw per-90 rates (found, during Task #4, to be far less sensitive to squad/league strength than raw volume) and does not use `PrgDist_Total` at all. |

### progressive_carrying

| Field | Content |
|---|---|
| Variable | `progressive_carrying` |
| Source | Derived, from Source A, stat block `possession` |
| Definition | Mean of three terms: `ratio(possession__PrgC_Carries, possession__Carries_Carries)`, `ratio(possession__Final_Third_Carries, possession__Carries_Carries)`, `ratio(possession__CPA_Carries, possession__Carries_Carries)` |
| Football meaning | The tendency to advance possession by dribbling/carrying rather than passing — progressive carries, carries into the final third, and carries into the penalty area, each as a share of the player's own total carries |
| Transformation | Ratio terms only (numerator/denominator, denominator 0 → NaN); concept score = mean of position-group z-scores; feeds `TD4_progression_carrying` (weight 1.0) |
| Limitations | Entirely unmeasurable for Sassuolo and Benevento — the `possession` block has 0% coverage in Serie A pre-2023/24 (D-006), and this concept's denominator (`possession__Carries_Carries`) as well as all three numerators come from that block. Not one of the 3 worked examples in `football_ontology.md` §3, so there is no earlier proposal to compare against. |

### possession_retention

| Field | Content |
|---|---|
| Variable | `possession_retention` |
| Source | Derived, from Source A, stat blocks `possession` and `passing` |
| Definition | Mean of three terms: `rate(possession__Touches_Touches)` (per-90), `asis(passing__Cmp_percent_Total)`, `asis(possession__Succ_percent_Take_Ons)` |
| Football meaning | Overall ball involvement (touches per-90) combined with passing accuracy and take-on success rate. Touches per-90 is deliberately kept as a raw rate rather than a share, because overall involvement/volume is itself part of what "retention-oriented" means football-wise (e.g. a deep-lying playmaker who touches the ball a lot) — there is no natural share denominator here that wouldn't just re-derive `Cmp_percent_Total` |
| Transformation | `rate` term = `col * 90 / Min`; `asis` terms used directly; concept score = mean of position-group z-scores. Not currently used as an input to any of the 7 `DIMENSION_WEIGHTS` dimensions except indirectly via `TD1_buildup_directness` (weight 0.3, changed from 0.4 under D-007) |
| Limitations | Entirely unmeasurable for Sassuolo and Benevento — both `possession` and `passing` blocks have 0% coverage in Serie A pre-2023/24 (D-006). The `rate` term (touches per-90, not possession-adjusted) can still carry a squad/league-strength confound that the ratio-based concepts are designed to reduce. |

### chance_creation

| Field | Content |
|---|---|
| Variable | `chance_creation` |
| Source | Derived, from Source A, stat block `passing` |
| Definition | Mean of two terms: `ratio(passing__KP, passing__Att_Total)` (key passes as a share of pass attempts), `ratio(passing__xA, passing__Att_Total)` (expected assists as a share of pass attempts) |
| Football meaning | How often a player's passing directly creates a scoring opportunity, independent of overall pass volume |
| Transformation | Ratio terms only; concept score = mean of position-group z-scores; feeds `TD6_chance_creation` (weight 0.7, alongside `crossing` at 0.3) |
| Limitations | The originally planned `summary__SCA_SCA`/`summary__GCA_SCA` (shot- and goal-creating actions) terms were **dropped**: the FBref match-level `summary` block is confirmed 0% populated for every league before season_end_year 2025, so it is entirely absent for this project's whole 2017/18–2023/24 in-scope window, for all three managers, not just Sassuolo/Benevento (this is a `summary`-block-wide gap, distinct from the ITA/FRA-specific `passing`/`possession`/`keeper` gap in D-006). `KP` and `xA` (both in the `passing` block) are the only chance-creation terms actually measurable in-window. Because they live in the `passing` block, this concept is still entirely unmeasurable for Sassuolo and Benevento specifically, on top of the summary-block gap affecting everyone. |

### box_presence

| Field | Content |
|---|---|
| Variable | `box_presence` |
| Source | Derived, from Source A, stat block `possession` |
| Definition | Single term: `ratio(possession__"Att Pen_Touches", possession__Touches_Touches)` — touches in the opponent's penalty area as a share of the player's total touches |
| Football meaning | How often a player is present and receiving the ball in the box, as a share of their overall involvement — box **occupation**, not shot quality or finishing |
| Transformation | Ratio term only; concept score = position-group z-score of this single ratio; feeds `TD7_box_presence` (weight 1.0) |
| Limitations | The originally planned `summary__Sh`/`summary__SoT`/`summary__npxG_Expected` (shot volume, shots on target, non-penalty expected goals) terms were **dropped for the same reason as `chance_creation`**: no shooting-detail block exists at FBref match level for the in-scope window (a dedicated "shooting" release asset does not exist; shot data lives only in the unavailable `summary` block). `box_presence` in this project therefore measures box occupation only — a real, documented scope reduction, not a silent one. Additionally, this concept is entirely unmeasurable for Sassuolo and Benevento, since both numerator and denominator live in the `possession` block (0% coverage in Serie A pre-2023/24, D-006). |

### pressing_intensity

| Field | Content |
|---|---|
| Variable | `pressing_intensity` |
| Source | Derived, from Source A, stat blocks `defense` and `misc`, plus team-level possession data from `data/raw/fbref_season/team_possession.parquet` |
| Definition | Mean of five `padj_rate` (possession-adjusted per-90) terms: `defense__"Att 3rd_Tackles"`, `defense__"Mid 3rd_Tackles"`, `defense__Tkl_Tackles`, `defense__Int`, `misc__Recov` |
| Football meaning | The frequency of defensive engagement (tackles by pitch third, interceptions, recoveries), independent of whether the engagement succeeds; a higher tackling share in the attacking/middle third specifically (rather than the defensive third) indicates a player engaged in pressing the opponent's build-up rather than defending deep. Possession-adjusting the rate is itself football-motivated: a team that dominates the ball faces less opponent-in-possession time and so racks up fewer raw defensive actions for the same underlying pressing *intent*, so raw per-90 rates alone conflate "presses less" with "had less to press against" |
| Transformation | **Changed under D-007 (closes previously-open decision OD-5): each term's type changed from `rate` to `padj_rate`.** Each term is now `raw_per90 * padj_factor`, where `padj_factor = league_avg_opponent_possession / this_team's_opponent_possession` for that team/season/league, computed by `attach_possession_adjustment()` from the team-level `Poss` column in `data/raw/fbref_season/team_possession.parquet` (opponent-share rows only). A team whose opponents held *more* of the ball than the league average gets scaled up (its raw counts understate its pressing intent); a team whose opponents held less gets scaled down. If the team/season/league combination isn't found in that table (e.g. outside the big-5 leagues, or a season the table doesn't cover), `padj_factor` defaults to **1.0** — the term degrades gracefully to a plain unadjusted `rate`, not an error or a dropped row. Concept score = mean of position-group z-scores; feeds `TD9_pressing_intensity` (weight 1.0) |
| Limitations | `defense` and `misc` are the two stat blocks confirmed 100% populated across all leagues/seasons, so `pressing_intensity` is one of only two concepts (the other being `individual_defending`'s `asis` term) **unaffected** by the D-006 Serie A/Ligue 1 pre-2023/24 gap — fully measurable for Sassuolo and Benevento. Per D-007's evaluation, possession-adjustment materially improved this dimension's discriminative power (permutation importance grew from +2.55pp to +7.49pp, per the corrected figures in D-009, remaining by far the strongest dimension) but did not eliminate the squad-strength confound risk entirely — the adjustment corrects for *this team's opponents'* average possession share, not for other squad-quality effects. No StatsBomb-style "pressures" count exists in the Opta-derived match-level schema; this tackle/interception/recovery proxy is a considered substitute, not an equivalent. |

### individual_defending

| Field | Content |
|---|---|
| Variable | `individual_defending` |
| Source | Derived, from Source A, stat blocks `defense` and `possession` |
| Definition | Mean of two terms: `asis(defense__Tkl_percent_Challenges)` (tackle success % in defensive challenges) and `ratio(defense__"Tkl+Int", possession__Touches_Touches)` (tackles+interceptions as a share of the player's own touches) |
| Football meaning | Individual defensive duel activity and effectiveness, at both a success-rate level and a volume-relative-to-involvement level |
| Transformation | `asis` term used directly; `ratio` term = numerator/denominator; concept score = mean of position-group z-scores; feeds `TD11_individual_defending` (weight 0.7, alongside `aerial_play` at 0.3) |
| Limitations | **Partially available for Sassuolo and Benevento**: the `asis` term (`defense__Tkl_percent_Challenges`) comes from the always-populated `defense` block and remains usable, but the `ratio` term's denominator (`possession__Touches_Touches`) comes from the `possession` block, which has 0% coverage in Serie A pre-2023/24 (D-006) — so for those two clubs, `individual_defending` is computed from the single surviving term only, not the intended two-term mean. |

### aerial_play

| Field | Content |
|---|---|
| Variable | `aerial_play` |
| Source | Derived, from Source A, stat block `misc` |
| Definition | Mean of two terms: `rate(misc__Won_Aerial_Duels)` (per-90) and `asis(misc__Won_percent_Aerial_Duels)` |
| Football meaning | Aerial duel volume and success rate — a player's reliance on and effectiveness in aerial contests |
| Transformation | `rate` term = `col * 90 / Min`; `asis` term used directly; concept score = mean of position-group z-scores; feeds `TD11_individual_defending` (weight 0.3, alongside `individual_defending` at 0.7) |
| Limitations | `misc` is one of the two always-100%-populated stat blocks, so this concept is **fully measurable for Sassuolo and Benevento** as well as every other in-scope club — unaffected by the D-006 gap. Not one of the 3 worked examples in `football_ontology.md` §3. |

### crossing

| Field | Content |
|---|---|
| Variable | `crossing` |
| Source | Derived, from Source A, stat blocks `misc`, `possession`, and `passing` |
| Definition | Mean of two terms: `ratio(misc__Crs, possession__Touches_Touches)` (crosses as a share of total touches) and `ratio(passing__CrsPA, passing__Att_Total)` (crosses into the penalty area as a share of pass attempts) |
| Football meaning | Reliance on crossing, both as a share of overall involvement and as a share of passing output specifically |
| Transformation | Ratio terms only; concept score = mean of position-group z-scores; feeds `TD6_chance_creation` (weight 0.3, alongside `chance_creation` at 0.7) |
| Limitations | Entirely unmeasurable for Sassuolo and Benevento: although the `misc__Crs` numerator is always available, its denominator (`possession__Touches_Touches`) and both the numerator and denominator of the second term (`passing__CrsPA`, `passing__Att_Total`) come from the `possession`/`passing` blocks, which have 0% coverage in Serie A pre-2023/24 (D-006) — so both terms are unusable for those two clubs. |

### goalkeeper_distribution

| Field | Content |
|---|---|
| Variable | `goalkeeper_distribution` |
| Source | Derived, from Source A (FBref/Opta match-level), stat block `keeper`; for season-level data, the equivalent `keepers_adv` block, remapped to the `keeper__` prefix during loading so the same `CONCEPTS` definition resolves against either source without maintaining two parallel definitions (`src/season_features.py::build_season_league_dataset`) |
| Definition | Mean of three terms, all `asis` and all inverted: `asis(keeper__Cmp_percent_Launched)` (completion % of launched/long passes), `asis(keeper__Launch_percent_Passes)` (share of all passes that are launched/long), `asis(keeper__AvgLen_Passes)` (average pass length in yards) |
| Football meaning | How much a goalkeeper favours long/launched distribution versus short build-up play — the goalkeeper-as-auxiliary-defender/first-build-up-passer mechanism identified as a discriminator for Guardiola and De Zerbi specifically in the project's own qualitative research (`outputs/football_knowledge/manager_philosophy_hypotheses.md` §1.2/§3.2). Because all three terms are inverted, a **high** concept score means **more** build-up-oriented (short, frequent, accurate short distribution rather than long launches) |
| Transformation | All three terms used directly (`asis`), then negated (`invert: ["t0","t1","t2"]`) before z-scoring, so higher raw launch length/launch share/launch-completion% produce a **lower** score, and vice versa; concept score = mean of position-group z-scores; feeds `TD1_buildup_directness` (weight 0.2, new in D-007, alongside `progressive_passing` at 0.5 and `possession_retention` at 0.3) |
| Limitations | **New in D-007.** By construction, this concept is **NaN for every outfield player** — the `keeper`/`keepers_adv` stat block only contains rows for players who played in goal, so outfield players simply have no value to compute a term from. This is exactly why `build_dimension_scores()` was made NaN-aware per row (D-007's "necessary fourth change"): without that fix, `TD1_buildup_directness` would have silently gone to NaN for every outfield player the moment this concept was added, since the pre-D-007 version summed all weighted concepts unconditionally rather than renormalising over only the concepts available for that row. Also inherits the D-006 gap: for Sassuolo and Benevento, the `keeper` block has 0% coverage in Serie A pre-2023/24, same as `passing`/`passing_types`/`possession`, so `goalkeeper_distribution` is additionally unmeasurable for those two clubs' goalkeepers specifically. |

## Tactical dimensions

Tactical dimensions are computed by `build_dimension_scores()` in `src/football_features.py` as a weighted mean of the constituent concept z-scores (`sum(concept_score * weight) / sum(weights)`), using explicit, argued football-knowledge weights (open decision OD-4) rather than statistically fitted ones. Only **7 of the 14 dimensions** proposed in `outputs/football_knowledge/football_ontology.md` §2 (TD1–TD14) are actually implemented in `DIMENSION_WEIGHTS`; the rest (TD2 press resistance, TD5 possession volume/tempo, TD8 aerial/set-piece reliance, TD10 defensive block height/shape, TD12 attacking transition, TD13 defensive transition, TD14 compactness/shape) require team-level or opponent-relative context, or tracking/360 data, not yet built, and are deferred per the ontology's own §5 "open items."

### TD1_buildup_directness

| Field | Content |
|---|---|
| Variable | `TD1_buildup_directness` |
| Source | Derived — weighted combination of concept scores |
| Definition | **Changed under D-007**: `0.5 * progressive_passing + 0.3 * possession_retention + 0.2 * goalkeeper_distribution` (weights sum to 1.0), previously `0.6 * progressive_passing + 0.4 * possession_retention` |
| Football meaning | Build-up directness: possession-based/patient build-up vs. direct/long-passing approach (Plakias 2025 latent variable #1 equivalent), now extended to include the goalkeeper's own distribution style as a third, football-motivated contributor to how directly a team builds up play |
| Transformation | Weighted mean of the three constituent concepts' z-scores, divided by total weight (1.0) — but computed **NaN-aware per row** by `build_dimension_scores()` (a D-007 change, made necessary by adding `goalkeeper_distribution`): for any given player-match row, the weight of any concept that is NaN for that row is zeroed out and the remaining weights are renormalised over just the concepts actually available, rather than the whole dimension going to NaN. This matters specifically because `goalkeeper_distribution` is NaN for every outfield player by construction (see that concept's entry) — without the renormalisation, `TD1` would have silently gone to NaN for every outfield player in the dataset the moment the new concept was added; this was caught by inspecting intermediate output before shipping, not assumed correct. For outfield players, `TD1` is therefore effectively `progressive_passing` and `possession_retention` reweighted to sum to 1.0 (i.e. roughly 0.625/0.375); for goalkeepers with a `goalkeeper_distribution` value, all three concepts contribute at the stated 0.5/0.3/0.2 weights (subject to whichever of the other two are also available for that row) |
| Limitations | Inherits the limitations of all three constituent concepts — `progressive_passing` and `possession_retention` remain entirely unmeasurable for Sassuolo/Benevento, since both depend on the `passing`/`possession` blocks unavailable in Serie A pre-2023/24 (D-006); `goalkeeper_distribution` is likewise unmeasurable for those two clubs' goalkeepers (same D-006 gap, `keeper` block) and is NaN for every outfield player everywhere by construction, so its practical contribution to `TD1` is limited to the small number of goalkeeper rows in the sample. Weights (0.5/0.3/0.2) are hand-specified, not fitted or PCA-derived (OD-4). |

### TD3_progression_passing

| Field | Content |
|---|---|
| Variable | `TD3_progression_passing` |
| Source | Derived — weighted combination of concept scores |
| Definition | `1.0 * progressive_passing` (single-concept dimension) |
| Football meaning | Progression via passing — line-breaking, forward passing into the final third/box; central to Guardiola's third-man/half-space mechanisms and De Zerbi's reversal patterns per the manager-research hypotheses |
| Transformation | Equal to the `progressive_passing` concept score directly (weight 1.0, no blending) |
| Limitations | Same as `progressive_passing`: entirely unmeasurable for Sassuolo/Benevento (D-006, `passing` block). |

### TD4_progression_carrying

| Field | Content |
|---|---|
| Variable | `TD4_progression_carrying` |
| Source | Derived — weighted combination of concept scores |
| Definition | `1.0 * progressive_carrying` (single-concept dimension) |
| Football meaning | Progression via carrying/dribbling rather than passing; not an explicit Plakias (2025) 19-variable dimension — a tracking-derived addition per the literature gap analysis; Klopp hypothesised higher (front-three/full-back 1v1 carrying) |
| Transformation | Equal to the `progressive_carrying` concept score directly (weight 1.0) |
| Limitations | Same as `progressive_carrying`: entirely unmeasurable for Sassuolo/Benevento (D-006, `possession` block). |

### TD6_chance_creation

| Field | Content |
|---|---|
| Variable | `TD6_chance_creation` |
| Source | Derived — weighted combination of concept scores |
| Definition | `0.7 * chance_creation + 0.3 * crossing` (weights sum to 1.0) |
| Football meaning | Chance-creation volume and type (Plakias #6 type of attack, #7 crossing, #12 width of creative phase, #15 tendency to create final attempts, combined) |
| Transformation | Weighted mean of the two constituent concepts' z-scores, divided by total weight (1.0) |
| Limitations | Both constituent concepts (`chance_creation`, `crossing`) are entirely unmeasurable for Sassuolo/Benevento (D-006); `chance_creation` is additionally reduced project-wide (all three managers, whole in-scope window) by the `summary`-block-wide absence of SCA/GCA data. Weights (0.7/0.3) are hand-specified, not fitted (OD-4). |

### TD7_box_presence

| Field | Content |
|---|---|
| Variable | `TD7_box_presence` |
| Source | Derived — weighted combination of concept scores |
| Definition | `1.0 * box_presence` (single-concept dimension) |
| Football meaning | Box presence / attacking aggressiveness (Plakias #14 individual attacking actions, #18 attacking aggressively); discriminates by player role more than by manager alone, so position-aware normalisation is required (brief §21) |
| Transformation | Equal to the `box_presence` concept score directly (weight 1.0) |
| Limitations | Same as `box_presence`: measures box occupation only, not shot quality (summary block unavailable project-wide before 2025); entirely unmeasurable for Sassuolo/Benevento (D-006, `possession` block). |

### TD9_pressing_intensity

| Field | Content |
|---|---|
| Variable | `TD9_pressing_intensity` |
| Source | Derived — weighted combination of concept scores |
| Definition | `1.0 * pressing_intensity` (single-concept dimension) |
| Football meaning | Pressing intensity and height (Plakias #10, press: high vs. deep) — per the ontology, the single most contested measurement problem in the literature (no paper possession-adjusts it), and hypothesised to be the single most discriminating dimension for Klopp |
| Transformation | Equal to the `pressing_intensity` concept score directly (weight 1.0) |
| Limitations | Same as `pressing_intensity`: fully measurable for Sassuolo/Benevento (unaffected by D-006, since `defense`/`misc` are always populated). Previously the dimension most likely to carry a squad-strength confound because its rate was unadjusted for possession (OD-5); as of D-007, `pressing_intensity`'s terms are possession-adjusted (`padj_rate`, see that concept's entry), which closes OD-5 and measurably improved this dimension's discriminative power, though it does not eliminate every squad-strength confound (the adjustment corrects for opponent possession share specifically, not squad quality generally). |

### TD11_individual_defending

| Field | Content |
|---|---|
| Variable | `TD11_individual_defending` |
| Source | Derived — weighted combination of concept scores |
| Definition | `0.7 * individual_defending + 0.3 * aerial_play` (weights sum to 1.0) |
| Football meaning | Individual defending duels (Plakias #11 individual defending actions, #17 defending aggressively) combined with aerial-duel activity |
| Transformation | Weighted mean of the two constituent concepts' z-scores, divided by total weight (1.0) |
| Limitations | `aerial_play` is fully measurable for Sassuolo/Benevento (unaffected by D-006); `individual_defending` is only partially available for those two clubs (its `possession`-dependent ratio term drops out, leaving only the `asis` term, per that concept's entry above) — so `TD11` for Sassuolo/Benevento is a degraded blend, not a clean absence, unlike TD1/TD3/TD4/TD6/TD7. Weights (0.7/0.3) are hand-specified, not fitted (OD-4). Team-strength confound risk flagged in the ontology: weaker teams often show more duels out of necessity, not philosophy. |

## Evaluation statistics (not tactical features -- describe the model's own accuracy)

Added 2026-08-11 (`notebooks/04_player_manager_compatibility.ipynb` §2b, decision D-008). Saved to `outputs/tables/best_fit_significance_test.csv`.

| Field | Content |
|---|---|
| Variable | `observed_rate` |
| Source | Derived — share of the n=561 well-covered player-seasons whose single best-fit manager is the manager they actually played under |
| Definition | 0.4207 (42.1%) |
| Football meaning | None directly — this is a model-accuracy statistic, not a tactical measurement |
| Limitations | A single point estimate; see `bootstrap_ci_low`/`bootstrap_ci_high` for its precision |

| Field | Content |
|---|---|
| Variable | `bootstrap_ci_low`, `bootstrap_ci_high` |
| Source | Derived — 2.5th/97.5th percentile of 5000 bootstrap resamples (with replacement) of the n=561 best-fit rows |
| Definition | 0.3779, 0.4617 (a 95% confidence interval of [37.8%, 46.2%] around the observed rate) |
| Limitations | The interval is wide (8.5 percentage points end to end) given n=561 -- the point estimate 42.1% should not be treated as more precise than this interval implies |

| Field | Content |
|---|---|
| Variable | `empirical_chance_baseline` |
| Source | Derived — mean of 5000 permutations shuffling the true `actual_manager` label among the n=561 rows while holding the model's own `scored_against_manager` decision fixed |
| Definition | 0.3403 (34.0%) |
| Football meaning | The rate at which the model's decisions would match the true manager purely by chance, given this sample's actual manager mix (203/188/170 for De Zerbi/Klopp/Guardiola) -- more precise than the naive "1 in 3 for three classes" figure used elsewhere, because it reflects the sample's real class imbalance rather than assuming perfect balance |

| Field | Content |
|---|---|
| Variable | `p_value` |
| Source | Derived — share of the 5000 permutations (above) whose match rate met or exceeded the observed 42.1% |
| Definition | 0.0002 |
| Football meaning | None directly — statistical-significance statistic. p=0.0002 means only 1 of the 5000 permutations reached or exceeded the observed rate, i.e. the observed association between the model's best-fit decision and the true manager is very unlikely to be a sampling artefact of this particular n=561 sample |

## Descriptive team-structure supplement (not part of the compatibility score)

Added 2026-08-11 (`notebooks/04_player_manager_compatibility.ipynb` §7, decision D-008). Saved to `outputs/tables/manager_formation_profile.csv` (pooled per manager) and `manager_formation_profile_by_club_season.csv` (per club-season). Deliberately **not** folded into the 7 tactical dimensions or the compatibility score — see D-008 for why (only 22 club-seasons have this data, too small a population to z-score against safely, unlike the other 7 dimensions which are standardised against the full 11132-player-season universe).

| Field | Content |
|---|---|
| Variable | `modal_formation` |
| Source | `data/processed/player_match_manager.parquet` -- `Home_Formation`/`Away_Formation`, whichever belongs to the player's own team in that match (`Home_Away`) |
| Definition | The single most frequently used starting formation string (e.g. `4-3-3`) across the matches in the group |
| Football meaning | A manager's or club-season's default structural setup |
| Limitations | Only covers the 22 club-seasons across the 6 clubs in the manager-attributed match-level sample (Liverpool, Manchester City, Sassuolo, Benevento, Brighton & Hove Albion, Marseille) -- not available for the wider player universe. Recovered from a cached intermediate file after the live upstream source (a rolling, non-versioned GitHub release) moved past the 2018-2023 window this project needs (D-008) |

| Field | Content |
|---|---|
| Variable | `formation_stability` |
| Source | Derived — (matches played in the modal formation) / (total matches) |
| Definition | A 0-1 share; e.g. 0.865 means the modal formation was used in 86.5% of matches |
| Football meaning | How structurally settled a manager or club-season is -- high stability means one fixed system is used almost every match; low stability means the setup changes often |
| Limitations | Same coverage limitation as `modal_formation` |

| Field | Content |
|---|---|
| Variable | `n_distinct_formations` |
| Source | Derived — count of unique formation strings used across the matches in the group |
| Definition | An integer count (e.g. Klopp 8, Guardiola 10, De Zerbi 15, pooled across each manager's full tenure) |
| Football meaning | A second, complementary view of structural fluidity alongside `formation_stability` — a manager could in principle have low stability but only 2-3 formations in rotation, versus genuinely wide-ranging experimentation |
| Limitations | Same coverage limitation as `modal_formation`; sensitive to how many matches/seasons are pooled (more matches gives more opportunity to use more formations, all else equal) |

| Field | Content |
|---|---|
| Variable | `mean_back_line_size` |
| Source | Derived — first number parsed from each match's own formation string (e.g. `3` from `3-4-3`), averaged across matches in the group |
| Definition | A continuous value typically between 3 and 5 (e.g. Klopp 4.00, Guardiola 3.87, De Zerbi 3.81) |
| Football meaning | How often a back three versus a back four (or five) is used -- a value below 4.0 indicates meaningful back-three usage across the period, not just an occasional experiment |
| Limitations | Same coverage limitation as `modal_formation`. Formations with unusual notation (e.g. a front-loaded diamond) are parsed by their first number only, which is standard convention (defensive line count) but does not capture every structural nuance a formation string can encode |
