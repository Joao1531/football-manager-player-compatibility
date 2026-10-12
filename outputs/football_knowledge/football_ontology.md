# Football Knowledge Ontology (v0.1 — proposed)

**Purpose.** This is the Football Knowledge Layer specified in the project brief (§5–9): the structured mapping from raw metrics → football concepts → tactical dimensions that sits between the data and every downstream model. It is the artefact the project brief calls the "key innovation". This version is a proposal for approval, built from three inputs, not invented from scratch:

1. The **validated 19-dimension set** from Plakias et al. (2025, JPES) — published, discriminant-validated (90.8%/100%/97.2% correct classification), face-validated against named tactical traditions (see `outputs/literature/literature_review_synthesis.md` §1.2).
2. The **13-dimension cross-paper frequency table** synthesised across all 7 supplied papers (`literature_review_synthesis.md` §2).
3. Our own manager-specific research (`manager_philosophy_hypotheses.md`), which surfaced mechanisms the academic literature does not name explicitly (e.g. De Zerbi's goalkeeper-as-third-centre-back press-baiting) and confirmed which dimensions are expected to be load-bearing for separating these three managers specifically.

The brief's own starting ontology (§7) is retained as the top-level grouping (BUILD-UP, PROGRESSION, POSSESSION, CHANCE CREATION, ATTACKING, TRANSITIONS, DEFENDING) because it maps cleanly onto both Plakias's 19 and our manager research, and because a report reviewer already familiar with that vocabulary (it is standard in the literature) will find it legible.

## 1. Tier structure

```
RAW EVENTS / MATCH STATS  (Source A: FBref/Opta player x match; Source B: StatsBomb events)
        |
METRICS  (per-90 or per-possession counting stats — one row per football_metrics.csv entry)
        |
FOOTBALL CONCEPTS  (a named, football-meaningful construct built from 2-6 metrics)
        |
TACTICAL DIMENSIONS  (Plakias-anchored, bipolar where possible)
        |
MANAGER / PLAYER PROFILE  (a vector over tactical dimensions)
```

## 2. Tactical dimensions (top tier) — mapped to Plakias 2025 and our 7-paper synthesis

| # | Tactical dimension (this project) | Plakias (2025) equivalent latent variable(s) | Other literature support | Manager-research relevance |
|---|---|---|---|---|
| TD1 | **Build-up directness** | #1 Build up phase (possession-based ↔ direct/long-passing) | Recurs in 6/7 papers (`literature_review_synthesis.md` §2) | Guardiola & De Zerbi hypothesised high (possession pole); Klopp lower — see H-B1/H-B3 |
| TD2 | **Press resistance** | Not a named Plakias variable directly; closest is #1 (build-up) combined with #10 (press) read from the *opponent's* side | Bolin & Vesterlind possession-chain features; Baattite EFA factors | De Zerbi's signature mechanism (§3.2 of philosophy file); expected high for Guardiola & De Zerbi |
| TD3 | **Progression (passing)** | Partially #1, #16 (tempo) | Recurs in nearly all papers under "progressive passing"/"line-breaking" | Central to Guardiola's third-man/half-space mechanisms and De Zerbi's reversal patterns |
| TD4 | **Progression (carrying)** | Not explicit in Plakias 19 — a tracking-derived addition (per literature gap analysis) | Bolin & Vesterlind, Tang et al. | Klopp hypothesised higher (front-three/full-back 1v1 carrying) — H-C3 tests the De Zerbi central-carry claim specifically |
| TD5 | **Possession volume/tempo** | #13 Effective game; #16 Passing tempo (note reversed polarity, flagged in literature review) | Universal across corpus | Use cautiously — team-strength confound flagged in philosophy file §4.4-1 |
| TD6 | **Chance creation volume & type** | #6 Type of attack; #7 Crossing; #12 Width of creative phase; #15 Tendency to create final attempts | Universal | Klopp: high, crossing-heavy (era-dependent, see H-C1); Guardiola: high, cut-back/central-preferred; De Zerbi: medium-high |
| TD7 | **Box presence / attacking aggressiveness** | #14 Individual attacking actions; #18 Attacking aggressively | Recurs as "box occupation" | Discriminates strikers/wide players by role more than by manager alone — position-aware normalisation required (brief §21) |
| TD8 | **Aerial / set-piece reliance** | #5 Aerial game; #6 Type of attack (set pieces pole); #19 Offside trap | Recurs in 6/7 papers | Expected low for all three (all are possession/combination-oriented managers) — a dimension more useful for excluding false positives than discriminating our three |
| TD9 | **Pressing intensity & height** | #10 Press (high ↔ deep) | Universal, and the single most contested measurement problem in the literature (no paper possession-adjusts it) | **The single most discriminating dimension for Klopp** (H-P1); expected surprisingly *low* for De Zerbi despite his attacking reputation (H-P3 — a genuinely testable, non-obvious claim) |
| TD10 | **Defensive block height/shape** | #9 Defensive blocks (mid ↔ low) | Recurs in 5/7 papers | Weakest-evidenced dimension for De Zerbi specifically (flagged gap, philosophy file §3.6/§4.4-6) |
| TD11 | **Individual defending (duels)** | #11 Individual defending actions; #17 Defending aggressively (reversed polarity!) | Universal | Team-strength confound risk (weaker teams often show more duels out of necessity, not philosophy) |
| TD12 | **Transition — attacking** | #3 Attacking transition (counterattack ↔ positional attack) | Universal | Klopp's organising principle (H-T1); De Zerbi's "possessional transition" claim is a hypothesis this dimension is specifically built to test (H-T2) |
| TD13 | **Transition — defensive** | #4 Defensive transition | Recurs in 5/7 papers | Rest-defence shape (Guardiola 3-2 vs Klopp 2-3, per Coaches' Voice) is a candidate sub-feature |
| TD14 | **Compactness / team shape** | *Not covered by Plakias* — tracking-derived addition | Tang et al.; Bolin & Vesterlind | Available only if StatsBomb 360/tracking-adjacent freeze-frame data is used; likely out of scope for the 2-week timeline (flagged, not committed) |

Dimensions TD1–TD13 are directly constructible from the Source A (FBref/Opta match-level) feature set audited in `outputs/audit/data_availability_matrix.md`. TD14 requires tracking or 360 data and is flagged as a stretch goal, not a committed deliverable, given the two-week scope (brief §45, "SHOULD/NICE TO HAVE").

## 3. Metric → Concept → Dimension worked examples

Full definitions for every concept will be maintained in `data_dictionary.md` (per brief §44) as the feature-engineering notebook is built (Task #3). Three worked examples here, in the exact format the brief requires (§9):

### Concept: Progressive Passing
| Field | Content |
|---|---|
| Definition | The tendency of a player to advance team possession meaningfully upfield via passing, rather than merely retaining it. |
| Underlying metrics (Source A columns) | `Prog` (progressive passes, passing.rds/passing_player match-level), `PrgDist_Total` (progressive pass distance), `Final_Third` (passes into the attacking third), `PPA` (passes into the penalty area), `Cmp_percent_Total` (completion %, as a quality control) |
| Football meaning | A high value indicates a player is a primary vehicle for moving the team from its own half into dangerous territory through passing rather than dribbling. |
| Calculation | Per-90 rate for each raw metric, then combined (see Task #3 for the exact weighting/PCA approach — not yet decided, see open decision OD-4) |
| Normalisation | Per-90 (minutes-adjusted); position-aware z-score within positional group (defenders vs midfielders vs attackers) per brief §21–22 |
| Literature support | Universal across the 7-paper corpus under "progressive passing"/"line-breaking actions" (`literature_review_synthesis.md` §2); maps to Plakias TD1/TD3 |
| Limitations | Raw progressive-pass counts conflate a hopeful long ball forward with a controlled line-breaking pass into a teammate under pressure — Opta's schema does not distinguish these; `Cmp_percent` is included specifically as a partial control for this |

### Concept: Pressing Intensity
| Field | Content |
|---|---|
| Definition | The frequency and location of a player's defensive engagement immediately after losing possession or against an opponent in possession, independent of whether the engagement succeeds. |
| Underlying metrics (Source A columns) | `Tkl_Tackles`, `Att 3rd_Tackles` + `Mid 3rd_Tackles` (high-pitch tackling location), `Int`, `Recov` (misc table), `TklW_Tackles` |
| Football meaning | High values in the attacking/middle third specifically (not the defensive third) indicate a player engaged in pressing the opponent's build-up rather than defending deep. |
| Calculation | Per-90 rate; a "high press" sub-score computed from `(Att 3rd_Tackles + Mid 3rd_Tackles) / Tkl_Tackles` to capture *where* the tackling happens, not just how much |
| Normalisation | Per-90; **NOT possession-adjusted in the first iteration**, flagged explicitly as a literature-identified gap (`literature_review_synthesis.md` §2, "no paper possession-adjusts pressing metrics") — the project should attempt possession-adjustment (pressing actions per opponent-possession, not per-90) as a methodological improvement over the literature, time permitting (open decision OD-5) |
| Literature support | Universal (TD9); explicit measurement caveat is itself a literature-documented gap, making this a candidate area of methodological contribution |
| Limitations | Opta's match-level schema (confirmed by direct inspection, see data availability audit §3) does not publish a StatsBomb-style "pressures" count; this proxy is a considered substitute, not equivalent, and must be documented as such |

### Concept: Build-up Goalkeeper/Defender Involvement
| Field | Content |
|---|---|
| Definition | The extent to which a team's goalkeeper and centre-backs function as active short-passing participants in the first phase of possession, rather than as a purely defensive/clearing unit. |
| Underlying metrics (Source A columns) | Goalkeeper table: `Cmp_percent_Launched` (inverted — low launch % = more short distribution), `AvgLen_Passes`/`AvgLen_Goal_Kicks` (lower = shorter, more build-up-oriented), `Launch_percent_Goal_Kicks`; outfield: `Touches_Def 3rd`, `Cmp_percent_Short` for centre-backs specifically |
| Football meaning | This is the metric-level anchor for what our manager research (§1.2, §3.2 of `manager_philosophy_hypotheses.md`) identifies as the single clearest *shared* mechanism between Guardiola and De Zerbi, and the clearest point of contrast with Klopp. |
| Calculation | Team-level aggregate for the season/window in question; player-level version restricted to goalkeepers and centre-backs |
| Normalisation | Not per-90 (these are rate/percentage metrics already); no further normalisation needed beyond position restriction |
| Literature support | Not explicitly named as a single construct in the 7-paper corpus (a genuine gap — none of the papers isolate goalkeeper distribution as a style-defining feature) — this concept is derived primarily from our own manager research rather than the academic literature, and should be flagged as such in the report for honesty (per brief §26, distinguishing data-derived vs. football-interpretation vs. project-derived evidence) |
| Limitations | Goal-kick length is influenced by opposition pressing height as well as by the team's own intent — a team facing a low block will naturally play shorter regardless of philosophy; ideally opponent-adjusted, not committed for v1 |

## 4. Position-aware handling (brief §21)

Per-90 raw values will be z-scored **within positional group**, not globally, before being combined into concept scores. Proposed positional groups (from Opta's `Pos` field, which uses standard abbreviations GK/DF/MF/FW with sub-codes):

- Goalkeeper (GK)
- Centre-back (DF, central sub-code)
- Full-back/wing-back (DF, wide sub-code)
- Defensive/central midfielder (MF, DM/CM sub-code)
- Attacking midfielder / winger (MF/FW, AM/wide sub-code)
- Striker/forward (FW, central sub-code)

This directly avoids the brief's own stated failure mode (§21): "this striker is similar to this midfielder because both have high passing volume." Exact sub-code parsing rules will be finalised in Task #3 once the raw `Pos` field's value distribution is inspected.

## 5. Open items for this ontology (feed into Phase 0 open decisions)

1. TD2 (press resistance) and the goalkeeper/CB build-up concept above are **not** directly named in the academic literature — they are added from our own manager research. This is intellectually honest (the brief explicitly wants football knowledge, not only literature, to drive feature engineering) but must be clearly labelled as such in the report, not presented as literature-derived.
2. TD14 (compactness/shape) requires tracking-adjacent data not committed in the current data scope — proposed as an explicit stretch goal, not a v1 commitment.
3. The exact aggregation method from Concept → Dimension (weighted sum? PCA loading? expert-assigned weights?) is deliberately left open here — this is a Task #3/#4 decision, informed by the literature's PCA/EFA consensus (`literature_review_synthesis.md` §2) but not yet fixed, pending the user's view on how much weight to give the "explicit, hand-specified football knowledge" approach vs. a "let PCA discover the weights" approach. **This is open decision OD-4.**
