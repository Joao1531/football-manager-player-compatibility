# Project Plan

## Objective
Investigate whether football knowledge and player performance data can be combined with machine learning to model the playing philosophies of Pep Guardiola, Jürgen Klopp and Roberto De Zerbi, and to estimate — explainably — how well an individual player fits each manager's football philosophy. Delivered as a MIAD final-project memoria in 3 escalones, structured around CRISP-DM (mandatory per `Guidelines/Estructura de documentacion TFM.pdf` and `Guidelines/MIAD TFM_ Exemplos propostas final project.pdf`).

## Current phase
**CRISP-DM phases 1-4 (Business/Data Understanding, Data Preparation, Modelling) complete for a v1 pipeline; Evaluation phase surfaced a significant, honestly-diagnosed limitation.** See `outputs/results/task4_evaluation_findings.md` §7 for three concrete options on how to proceed — this is the current decision point, not yet resolved.

## Completed
- Read both Guidelines PDFs (CRISP-DM + 3-escalón structure is a hard deliverable requirement; two of the official example proposals directly anticipate this project's theme).
- Read and synthesised all 7 supplied papers (`outputs/literature/literature_review_synthesis.md`).
- Built a verified, source-corroborated manager tenure table with match-level attribution hazards flagged (`data/external/manager_tenures.md`/`.csv`).
- Researched and sourced tactical philosophy profiles for all three managers, with an explicit stable-vs-contingent split and a falsifiable-hypothesis set (`outputs/football_knowledge/manager_philosophy_hypotheses.md`).
- Audited two public data sources directly (StatsBomb Open Data; FBref/Opta match-level via `worldfootballR_data`) and built a manager × team × season availability matrix (`outputs/audit/data_availability_matrix.md`).
- Drafted a football knowledge ontology anchored on a validated, published 19-dimension set (Plakias et al. 2025) plus our own manager research (`outputs/football_knowledge/football_ontology.md`).
- Scaffolded the project directory structure (data/, notebooks/, src/, outputs/, models/, report/) and a reproducible data-access module (`src/data_sources.py`).
- Actively chased additional historical sources for Bayern/Dortmund/Palermo/Shakhtar per explicit request; confirmed the gaps are genuine data non-existence; found and added a usable Benevento 2017/18 correction (`data_availability_matrix.md` §4).
- Built the manager-attributed match-level dataset (`notebooks/02_data_collection_and_manager_attribution.ipynb`): match-date-based splitting for every mid-season tenure change, integrity audit passed clean (zero out-of-window rows, zero duplicates).
- Implemented the Football Knowledge Layer (`notebooks/03_football_feature_engineering.ipynb`, `src/football_features.py`): 9 concepts, 7 tactical dimensions, position-aware + league-population-baseline z-scoring, PCA coherence checks.
- Built the player→manager compatibility model, explanations, and club-identity-bias check (`notebooks/04_player_manager_compatibility.ipynb`, `src/compatibility.py`).
- **Found and fixed two significant data-integrity bugs during evaluation** (a `fillna(0)` silently treating missing data as "exactly average"; a previously-undetected FBref coverage gap for Serie A/Ligue 1 pre-2023/24) — see `decision_log.md` D-006. Post-fix, the honest result is that the v1 feature set does not discriminate the three managers better than chance (32.8% best-fit match rate vs ~33% baseline) and the club-bias check still shows squad/league strength dominating over managerial signal.

## Current task
Decide how to proceed given the Task #4 finding — see `outputs/results/task4_evaluation_findings.md` §7 (options a/b/c: accept and report as a limitation-rich finding; attempt a team-strength-residualised feature redesign; or narrow the quantitative claim to pressing/defending dimensions only). This is the current decision point.

## Next tasks (depend on the decision above)
1. Depending on the choice above: either move to report-writing, or implement the team-strength-residualised feature redesign and re-run the evaluation.
2. Explainability polish (SHAP/permutation importance on top of the current contribution-decomposition explanations, per the two-week scope triage already agreed).
3. Write the memoria (3 escalones) + explanatory CRISP-DM video + bibliography PDF + finalise notebooks.

## Deadline
~2 weeks from project start (2026-08-10). CRISP-DM video and 3-escalón memoria are both mandatory deliverables per the Guidelines, in addition to notebooks, datasets, papers and a bibliography PDF.

## Risks
- **Asymmetric club coverage**: Guardiola and Klopp's open-data-covered windows are single-club (Man City, Liverpool respectively); only De Zerbi's spans multiple clubs/leagues. Direct consequence of FBref match-level data starting in 2017/18. Mitigation proposed in `outputs/audit/data_availability_matrix.md` §2.
- **Pressing-metric proxy**: Opta's match-level schema has no direct "pressures" count; pressing intensity must be approximated from tackle-location + interceptions + recoveries. Documented in `football_ontology.md` §3.
- **Two-week timeline** vs. the breadth of the brief (§45 MUST/SHOULD/NICE-TO-HAVE triage will need active management — see open decision OD-6).
- **Background-agent cost**: one research agent was terminated mid-task by the organisation's monthly Claude API spend limit (2026-08-10). Remaining research is being done via direct foreground tool calls to avoid repeating this; if the limit recurs it will slow, not block, progress.

## Open questions
See `outputs/PHASE0_DELIVERABLE.md` §"Open decisions requiring approval" — OD-1 through OD-6.
