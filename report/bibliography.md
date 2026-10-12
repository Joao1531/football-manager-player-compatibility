# Bibliography

Consolidated from all research conducted for this project. Three categories, each sourced from a specific project artefact — no reference below was fabricated or supplied from memory; every entry is traceable to the file noted.

## 1. Academic literature (the 7 supplied papers)

Full BibTeX, reading provenance, and per-paper structured summaries: [`outputs/literature/literature_review_synthesis.md`](../outputs/literature/literature_review_synthesis.md) (§1 for summaries, bibliography block near the end of the file for BibTeX).

```bibtex
@article{gu2025playingstyle,
  author  = {Gu, Linda and Wang, Wenlong and Plakias, Spyridon and Zhang, Shaoliang},
  title   = {Playing style identification in team sports: A systematic review from statistical dimensionality reduction to unsupervised machine learning},
  journal = {International Journal of Sports Science \& Coaching},
  year    = {2025},
  pages   = {1--20},
  doi     = {10.1177/17479541251372586}
}

@article{plakias2025overallstyles,
  author  = {Plakias, Spyridon and Armatas, Vasilis and Mprotsis, Theodoros and Kyranoudis, Angelos and Gu, Linda and Xylomenos, Fotios and Michailidis, Yiannis},
  title   = {What playing styles best represent the overall tactical identity of European soccer teams?},
  journal = {Journal of Physical Education and Sport (JPES)},
  year    = {2025},
  volume  = {25},
  number  = {11},
  pages   = {2249--2257},
  doi     = {10.7752/jpes.2025.11248}
}

@article{zhong2026classification,
  author  = {Zhong, Yonghan and Xu, Ying and Zhu, Kecheng and Diaz-Cidoncha Garcia, Jorge and G{\'o}mez Ruano, Miguel {\'A}ngel and Yi, Qing},
  title   = {Data-driven classification of playing styles and match outcome prediction in {UEFA} {C}hampions {L}eague teams},
  journal = {Biology of Sport},
  year    = {2026},
  volume  = {43},
  pages   = {575--586},
  doi     = {10.5114/biolsport.2026.154944}
}

@mastersthesis{bolin2025patterns,
  author = {Bolin, Niklas and Vesterlind, Elliot},
  title  = {From Patterns to Playbooks: Identifying offensive and defensive team playing styles from possession chains with machine learning and its possible practical applications in management of football teams},
  school = {Uppsala University, Faculty of Science and Technology},
  year   = {2025},
  month  = jun,
  number = {UPTEC I 25002}
}

@misc{tang_clustering_situations,
  author = {Tang, Zitian and Wang, Xing and Zhang, Shaoliang},
  title  = {Clustering Football Game Situations via Deep Representation Learning},
  note   = {Venue, year and DOI not stated in the supplied PDF}
}

@techreport{baattite2023mlfootball,
  author      = {Baattite, Anass},
  title       = {Machine Learning-Based Football Tactic and Style Analysis},
  institution = {School of Science and Engineering, Al Akhawayn University},
  year        = {2023},
  type        = {Capstone Design Final Report}
}

@misc{wang2023tacticai,
  author        = {Wang, Zhe and Veli{\v c}kovi{\'c}, Petar and Hennes, Daniel and Toma{\v s}ev, Nenad and Prince, Laurel and Kaisers, Michael and Bachrach, Yoram and Elie, Romuald and Wenliang, Li Kevin and Piccinini, Federico and Spearman, William and Graham, Ian and Connor, Jerome and Yang, Yi and Recasens, Adri{\`a} and Khan, Mina and Beauguerlange, Nathalie and Sprechmann, Pablo and Moreno, Pol and Heess, Nicolas and Bowling, Michael and Hassabis, Demis and Tuyls, Karl},
  title         = {TacticAI: an AI assistant for football tactics},
  year          = {2023},
  month         = oct,
  eprint        = {2310.10553},
  archivePrefix = {arXiv},
  primaryClass  = {cs.LG}
}
```

**Chase-list (cited by the reviewed papers, not yet read for this project — flagged in `literature_review_synthesis.md` §4 as worth pursuing if the project continues):** Cintia & Pappalardo, *Coach2vec* (arXiv:2106.15444) — models coach-level style directly and must be read before any novelty claim about manager-level modelling is finalised; Plakias, Kokkotis et al. (2023) — the original source of the 19 latent variables reused by Plakias et al. (2025); Rein & Memmert (2016) — cited as the strongest argument for why a knowledge layer is needed at all.

## 2. Manager tenure and tactical-philosophy sources

77 individually-attributed sources (club official statements, Wikipedia managerial records, Opta/StatsPerform analyst pieces, Coaches' Voice, Spielverlagerung, Total Football Analysis, and named press outlets), each corroborated against ≥2 independent sources per tenure claim. Full numbered list: [`data/external/manager_tenures.md`](../data/external/manager_tenures.md) §4 (77 sources) and [`outputs/football_knowledge/manager_philosophy_hypotheses.md`](../outputs/football_knowledge/manager_philosophy_hypotheses.md) (Sources sections, per manager).

Representative highlights (full list in the two files above):
- Perarnau, M. — *Pep Confidential*, cited via Perarnau Magazine (martiperarnau.com) for Guardiola's *juego de posición* framework.
- Coaches' Voice — "Pep Guardiola: Coach Watch" (2021); "The tactical evolution of Pep Guardiola's Manchester City" (2026); "Roberto De Zerbi tactics and style of play" (Brighton/Shakhtar/Sassuolo).
- Spielverlagerung — "Manchester City: Positional play analysis" (2017); "Previewing Pep Guardiola's Manchester City reign" (2016).
- Opta Analyst (theanalyst.com) — multiple data-confirmed statistical pieces on Guardiola's Manchester City tenure (2019-2025).
- SoccerTutor.com, Medium (SHfootball) — De Zerbi's goalkeeper/centre-back build-up mechanism.
- Wikipedia — managerial-statistics tables for Guardiola, Klopp, De Zerbi (tenure dates, cross-corroborated against club/press sources per `manager_tenures.md` §3's documented conflict-resolution log).

## 3. Data source documentation

- StatsBomb Open Data — `https://github.com/statsbomb/open-data` (competition/match manifests, event data, match-level manager attribution).
- `worldfootballR_data` (JaseZiv) — `https://github.com/JaseZiv/worldfootballR_data` (FBref/Opta match-level advanced statistics mirror; `fb_advanced_match_stats` release used as the primary source, per `decision_log.md` D-002).
- `soccerdata` Python package — tested for FBref/Understat access; FBref direct access blocked (HTTP 403) from this environment, Understat's schema insufficient alone (`outputs/audit/data_availability_matrix.md` §6).
- Kaggle "European Soccer Database" (Hugo Mathien) — investigated as a possible historical extension for Bayern/Dortmund; schema found insufficient (FIFA-video-game ratings and box-score events, not passing/pressing detail) — see `decision_log.md` D-005 for the full assessment.
