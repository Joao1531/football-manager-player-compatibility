# Phase 0 Deliverable — Project Audit, Data Feasibility & Proposed Methodology

Compiled 2026-08-10. This is the first deliverable requested before any ML implementation begins (project brief §46–47). It synthesises the standalone research artefacts already written; **follow the links for full detail** rather than expecting everything reproduced here.

## 1. Understanding of the project
A knowledge-informed ML system that models three managers' playing philosophies as measurable football dimensions, profiles individual players on the same dimensions, and computes an explainable compatibility score — with football knowledge as a first-class input to feature engineering and interpretation, not a post-hoc narrative layer. Report deliverable follows a mandatory 3-escalón structure (Directivo / Macro / Técnico) organised around CRISP-DM (`Guidelines/`).

## 2. Research question
"Given what we know about how Guardiola, Klopp and De Zerbi want their teams to play, and given what the player's data tells us about his football characteristics, which manager does he fit best — and why?" (brief §54, verbatim).

## 3. Hypotheses
H1–H4 as proposed in the brief (§37) are adopted, refined with the falsifiable, dimension-level hypotheses in [`outputs/football_knowledge/manager_philosophy_hypotheses.md`](football_knowledge/manager_philosophy_hypotheses.md) §4.2 (H-P1–H-P3, H-B1–H-B3, H-C1–H-C3, H-T1–H-T2, H-X1–H-X2).

## 4. Literature findings
Full synthesis: [`outputs/literature/literature_review_synthesis.md`](literature/literature_review_synthesis.md) (~22,800 words, all 7 supplied papers read in full).

**Headline findings:**
- Team-level playing-style identification via PCA/EFA + clustering is mature and well-trodden (25-study systematic review, Gu et al. 2025). Our contribution must not be presented as inventing this.
- **Plakias et al. (2025, JPES)** provides a **published, discriminant-validated 19-dimension latent-variable set** (90.8–100% correct classification across 3 discriminant analyses, 174 teams/11 leagues) — adopted as the anchor for our ontology.
- That same paper **independently clusters Barcelona, Bayern Munich and Manchester City together** in a "structured positional play" style, and **Liverpool with Atalanta** in a "controlled possession + rapid counterattack" style — external, non-circular corroboration that our three managers (or at least Guardiola and Klopp's clubs) carry a detectable cross-club signal, even though our own model cannot fully test this for the open-data window (see §7 below).
- **Gap identified:** no paper models *manager*-level philosophy (all are team/club-level); none implement player→manager compatibility as we define it; none make the metric→concept→dimension mapping explicit and auditable. **TacticAI's (DeepMind/Liverpool FC) blinded 5-expert validation protocol** is the strongest available template for our own football-validation step.
- **Honesty flag:** Cintia & Pappalardo's *Coach2vec* (arXiv:2106.15444, not in our supplied corpus) already models coach-level style and must be read before any novelty claim is finalised in the report.

## 5–7. Manager tactical profile hypotheses (Guardiola, Klopp, De Zerbi)
Full sourced profiles, comparative matrix and falsifiable hypotheses: [`outputs/football_knowledge/manager_philosophy_hypotheses.md`](football_knowledge/manager_philosophy_hypotheses.md).

**Headline findings:**
- Guardiola and De Zerbi are expected to be the **hardest pair to separate** (both build deliberately through the goalkeeper/centre-backs, both use possession instrumentally) — the discriminating signal is expected to be *sequential/structural* (Guardiola's rigid positional grid vs. De Zerbi's press-baiting pause-and-invite), not raw volume, which has direct feature-engineering consequences.
- Klopp is expected to be the **easiest to separate**, via pressing intensity and transition speed — both well-measured by standard event data.
- Each manager shows at least one **documented within-tenure regime shift** that must not be pooled into one stationary profile: Guardiola's false-9 → Haaland target-man reversal; Klopp's crossing-heavy → central-underlap shift (2023/24); De Zerbi's Sassuolo (fragile defensively) vs. Brighton/Marseille (better resourced).
- De Zerbi's out-of-possession/pressing profile is the weakest-evidenced section of the current research (a follow-up search is recommended, not yet done — see open decision OD-1).

## 8. Manager-tenure table
[`data/external/manager_tenures.md`](../data/external/manager_tenures.md) / [`.csv`](../data/external/manager_tenures.csv). 21 tenure rows, each corroborated against ≥2 independent sources, with an explicit attribution-safety grade (SAFE / CAUTION / UNSAFE-must-split-at-match-level / EXCLUDE) and a documented list of source conflicts.

## 9. Data availability matrix
[`outputs/audit/data_availability_matrix.md`](audit/data_availability_matrix.md). Two sources audited **directly** (downloaded and queried, not assumed from documentation):
- **StatsBomb Open Data**: 80 competition-seasons; Guardiola well-covered only at Barcelona (132 team-matches, 4 complete La Liga seasons); Klopp poorly covered (33 team-matches total, mostly the 2015/16 Liverpool arrival slice); **De Zerbi has zero matches in StatsBomb Open Data**.
- **FBref/Opta match-level** (via the public `worldfootballR_data` repository release assets): covers 5 big leagues, **Season_End_Year 2018–2026 (2017/18 season onward)**, confirmed by direct file inspection. Covers Man City (Guardiola), Liverpool (Klopp), and Sassuolo/Brighton/Marseille (De Zerbi) well; does **not** reach Barcelona, Bayern, or Dortmund (all pre-2017/18).

## 10–11. Recommended seasons and teams
| Manager | In-scope clubs | In-scope seasons | ~Matches |
|---|---|---|---|
| Guardiola | Manchester City | 2017/18–2023/24 (7 seasons) | ~266 |
| Klopp | Liverpool | 2017/18–2023/24 (7 seasons) | ~266 |
| De Zerbi | Sassuolo, Benevento (flagged low-confidence), Brighton, Marseille | Sassuolo 2018/19–2020/21; Benevento 2017/18 (part, ~28 matches); Brighton 2022/23(part)–2023/24; Marseille 2024/25–2025/26(part) | ~260 |

Full justification and excluded-tenure rationale: `data_availability_matrix.md` §2. **Update (2026-08-10):** per the user's explicit request, an active search for additional sources covering Bayern Munich, Dortmund, Palermo and Shakhtar was carried out (not just deprioritised) — see `data_availability_matrix.md` §4. It confirmed these gaps are genuine data-non-existence, not a sourcing failure, with one concrete correction found in the process: Benevento 2017/18 is usable and has been added above.

## 12–13. Candidate football dimensions and ontology
[`outputs/football_knowledge/football_ontology.md`](football_knowledge/football_ontology.md). 14 tactical dimensions (TD1–TD14), 13 directly constructible from the in-scope data, anchored on Plakias et al.'s validated 19-variable set plus manager-research additions (explicitly flagged as project-derived where the literature doesn't name them, e.g. press resistance, goalkeeper/CB build-up involvement). Three fully worked metric→concept→dimension examples included (Progressive Passing, Pressing Intensity, Build-up Goalkeeper/Defender Involvement).

## 14. Candidate features
Enumerated per Source A stat block in `data_availability_matrix.md` §3 and `data_sources.py`; full raw-to-concept mapping to be completed in `data_dictionary.md` during Task #3.

## 15. Candidate ML methods
Per the literature consensus (`literature_review_synthesis.md` §2): PCA/EFA with Varimax rotation for dimensionality reduction (44% of reviewed studies, the modal choice), followed by k-means or Ward hierarchical clustering for style discovery, validated via discriminant analysis (Plakias's own template) rather than only internal indices. For the compatibility model specifically: similarity/distance-based scoring (cosine or Mahalanobis distance from player profile to manager centroid) is the leading candidate over a supervised classifier, because a classifier needs the very manager-label-contamination risks the club-bias check is designed to catch. **Not yet fixed — open decision OD-4.**

## 16. Evaluation strategy
Combine: (a) internal cluster validity (silhouette, Davies-Bouldin — explicitly absent from all 7 corpus papers, a chance to exceed the literature's own standard); (b) discriminant-analysis-style external validity (Plakias's template); (c) a club-identity-bias check via **within-club, different-manager natural experiments already confirmed in the data** — Liverpool 2015/16 (Rodgers 8 games → Klopp 30 games, same club/season/squad) and Barcelona's multi-manager history (Guardiola/Luis Enrique/Valverde/Rijkaard, same club across different managers) — both directly queryable from StatsBomb Open Data as a genuine leave-one-club-out-style control (brief §19); (d) a TacticAI-style football-expert face-validation pass on a sample of outputs, time permitting.

## 17. Bias risks
Full list in `manager_philosophy_hypotheses.md` §4.4: team-strength confound (Guardiola/Klopp elite squads), team-weakness confound cutting the other way (De Zerbi's Sassuolo/Benevento), mid-season contamination (mitigated by D-004), within-manager regime shifts (false-9→Haaland; crossing→central-underlap), "false control" seasons (Vilanova/Maresca/Potter successions), and — the central one — **club-identity bias**, for which Guardiola's and Klopp's in-scope samples are single-club (a genuine, documented asymmetry vs. De Zerbi's three-club sample), mitigated per §7 of the availability matrix.

## 18. Data leakage risks
No temporal leakage risk identified yet (this is a profiling/similarity task, not a forecasting task, so train/test leakage in the traditional sense is less central) — but **manager-label leakage via club identity** is the analogous risk here and is treated as the primary evaluation target (§16c) rather than an afterthought.

## 19. Project architecture
Directory structure scaffolded (`data/`, `notebooks/`, `src/`, `outputs/`, `models/`, `report/`); reproducible data-access layer written (`src/data_sources.py`, covering both sources with cached downloads); `project_plan.md`, `decision_log.md` (5 entries so far), `data_dictionary.md` (skeleton) established per brief §44.

## 20. Two-week plan
1. **Days 1–2 (today, done):** business/data understanding — this deliverable.
2. **Days 2–4:** data preparation — build the manager-attributed match-level dataset with match-date-based splitting, run the integrity audit (Task #2).
3. **Days 4–7:** feature engineering — implement the Football Knowledge Layer as a notebook module, resolve OD-4/OD-5 (Task #3).
4. **Days 7–10:** modelling — manager profiles, player profiles, compatibility scoring, club-bias validation (Task #4).
5. **Days 10–12:** explainability + evaluation, football-validation pass.
6. **Days 12–14:** memoria (3 escalones), CRISP-DM video script, bibliography PDF, notebook cleanup for reproducibility (Task #5).

## 21. Open decisions — status

**OD-2 — RESOLVED (chased, not just accepted).** User asked to actively chase additional sources for Bayern/Dortmund/pre-Sassuolo De Zerbi before accepting the scope limitation. Done: FBref's own historical depth tested empirically (0% xG coverage for Bundesliga 2013/14–2015/16), the `worldfootballR_data` `match_results` release checked (scores only, no tactical detail), the Kaggle "European Soccer Database" (2008–2016 coverage) located and its schema verified as FIFA-ratings + box-score events only (not passing/pressing detail, and non-poolable with the primary dataset regardless per D-003), and Ukrainian-league/Palermo alternatives searched with no result. **Conclusion: the gaps are genuine data non-existence, confirmed rather than assumed.** One correction found in the process: Benevento 2017/18 is usable and has been added to the in-scope De Zerbi sample (§10–11 above, flagged low-confidence). See `data_availability_matrix.md` §4 and `decision_log.md` D-005 for full detail.

**OD-4 — RESOLVED.** Hybrid aggregation confirmed: PCA/EFA validates that hand-grouped metrics-within-concepts are statistically coherent; explicit, argued weights combine concepts into tactical dimensions. To be implemented in Task #3.

**OD-6 — RESOLVED.** Position-aware modelling and SHAP-based explainability are committed in-scope (SHOULD-HAVE). Player archetypes, deep learning/embeddings, and any dashboard/web app remain explicitly out of scope (NICE-TO-HAVE, deferred) for this timeline.

**OD-1 and OD-3 — still open, lower stakes, proceeding on the stated recommendation unless redirected:** De Zerbi's out-of-possession profile will be closed with a bounded follow-up during Task #3/#4 rather than blocking now; the supplementary StatsBomb Barcelona robustness analysis (OD-3) will be attempted only if time permits after the core Task #2–4 pipeline works.

**OD-5 — still open, proceeding on recommendation:** possession-adjusted pressing metrics will be attempted in Task #3 as a documented methodological improvement over the literature's own gap.

---
*Per brief §46, no ML implementation has begun yet. All blocking open decisions are now resolved — proceeding to Task #2 (manager-attributed dataset construction).*
