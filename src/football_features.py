"""
Football Knowledge Layer: raw metrics -> football concepts -> tactical
dimensions -> player/manager profiles.

Implements the ontology in outputs/football_knowledge/football_ontology.md
and the hybrid aggregation method decided in outputs/PHASE0_DELIVERABLE.md
(open decision OD-4): PCA validates that hand-grouped metrics cohere
statistically within a concept; explicit, argued weights then combine
concepts into tactical dimensions.

Column-naming note: the merged player x match dataset
(data/processed/player_match_manager.parquet) carries some duplicate-named
columns inherited from FBref's own grouped-header tables (e.g. a
"defense__Att.3rd_Tackles" alongside "defense__Att 3rd_Tackles"). The
space-separated names are the canonical ones (verified by non-null coverage
-- the dotted variants are near-empty scrape artefacts); only canonical
names are referenced below.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# --------------------------------------------------------------------------
# 1. Position grouping (brief SS21-22)
# --------------------------------------------------------------------------
# v1 used 4 coarse buckets (GK/Defender/Midfielder/Forward). A central
# midfielder, a defensive pivot and an attacking #10 have fundamentally
# different baselines on box presence, pressing and progression -- lumping
# them together is role noise sitting on top of (and likely obscuring) any
# managerial signal. This v2 refines to 8 role buckets using FBref's Pos tag
# (which lists a primary and, often, a secondary position, e.g. "DF,MF")
# combined with a touches-by-third zone heuristic where the tag alone is
# ambiguous -- e.g. a plain "DF" could be a stay-at-home centre-back or an
# advanced wing-back; their share of touches in the attacking third is very
# different and cheaply available. This is a transparent, documented
# heuristic, not a learned classifier -- it will misclassify some players,
# but should still be a large improvement over 4 buckets.

ROLE_GROUPS = [
    "Goalkeeper", "Centre-back", "Full-back/Wing-back", "Defensive Midfielder",
    "Central Midfielder", "Attacking Midfielder", "Winger/Second Striker", "Striker",
]

# Zone columns used for the refinement, as they appear after the standard
# stat-block prefixing (match-level) -- season-level data is renamed to the
# same names during the .rds -> .parquet conversion, so one heuristic works
# for both sources.
_ZONE_COLS = ["possession__Def 3rd_Touches", "possession__Mid 3rd_Touches", "possession__Att 3rd_Touches"]


def _attacking_third_share(df: pd.DataFrame) -> pd.Series:
    if not all(c in df.columns for c in _ZONE_COLS):
        return pd.Series(np.nan, index=df.index)
    total = df[_ZONE_COLS].sum(axis=1).replace(0, np.nan)
    return df["possession__Att 3rd_Touches"] / total


# Match-level FBref data tags a specific role per match (CB/LB/RB/WB/DM/CM/
# AM/LM/RM/LW/RW/FW/GK) -- much more informative than season-level's coarse
# DF/MF/FW/GK-only tagging (confirmed by direct inspection of both sources).
# Map the specific codes directly; only fall back to the zone-share
# heuristic for the coarse season-level codes, where no finer tag exists.
_FINE_GRAINED_MAP = {
    "GK": "Goalkeeper",
    "CB": "Centre-back",
    "LB": "Full-back/Wing-back", "RB": "Full-back/Wing-back", "WB": "Full-back/Wing-back",
    "DM": "Defensive Midfielder",
    "CM": "Central Midfielder",
    "AM": "Attacking Midfielder",
    "LM": "Winger/Second Striker", "RM": "Winger/Second Striker",
    "LW": "Winger/Second Striker", "RW": "Winger/Second Striker",
    "FW": "Striker",
}
_COARSE_CODES = {"DF", "MF", "FW", "GK"}


def position_group(df_or_pos) -> pd.Series:
    """Refined 8-way role grouping.

    Match-level data's specific position codes (CB/LB/RB/... ) are mapped
    directly (see _FINE_GRAINED_MAP). Season-level data only has the coarse
    DF/MF/FW/GK tags -- for those, falls back to a touches-by-third zone
    heuristic (a plain "DF" could be a centre-back or an advanced wing-back;
    their attacking-third touch share differs a lot and is cheap to use).
    Accepts either a full dataframe (needed for the zone fallback) or just
    the raw `Pos` series (used where zone columns are unavailable, e.g.
    Benevento match-level rows with no possession-block data at all -- see
    decision_log.md D-006; degrades to tag-only classification there).
    """
    if isinstance(df_or_pos, pd.Series):
        pos, att_share = df_or_pos, pd.Series(np.nan, index=df_or_pos.index)
    else:
        pos, att_share = df_or_pos["Pos"], _attacking_third_share(df_or_pos)

    pos = pos.fillna("MF")
    tags = pos.str.split(",")
    primary = tags.str[0].str.strip()
    secondary = tags.apply(lambda t: t[1].strip() if len(t) > 1 else "")

    def classify(p, s, att):
        if p in _FINE_GRAINED_MAP:
            return _FINE_GRAINED_MAP[p]
        # Coarse (season-level) tags only from here on.
        if p == "DF":
            if s == "MF" or (pd.notna(att) and att > 0.28):
                return "Full-back/Wing-back"
            return "Centre-back"
        if p == "MF":
            if s == "DF":
                return "Defensive Midfielder"
            if s == "FW":
                return "Attacking Midfielder"
            if pd.notna(att):
                if att < 0.34:
                    return "Defensive Midfielder"
                if att > 0.55:
                    return "Attacking Midfielder"
            return "Central Midfielder"
        return "Central Midfielder"

    return pd.Series(
        [classify(p, s, a) for p, s, a in zip(primary, secondary, att_share)],
        index=pos.index,
    )


# --------------------------------------------------------------------------
# 2. Concept definitions: which raw columns, and how to turn them into a
#    scale-free number
# --------------------------------------------------------------------------
# Each term is one of:
#   ("rate", col)          -- a counting stat, converted to per-90.
#   ("ratio", num, denom)  -- num/denom, e.g. progressive passes as a SHARE
#                             of the player's own total passes. Ratios are
#                             deliberately preferred over raw per-90 volume
#                             wherever a sensible denominator exists (see
#                             outputs/results/task4_evaluation_findings.md
#                             SS3-4): a share answers "when this player acts,
#                             how often is it this kind of action?", which is
#                             far less sensitive to the surrounding team's
#                             overall possession/technical level than a raw
#                             per-90 count is -- v1 used raw per-90 counts
#                             throughout and the club-bias check in notebook
#                             04 showed this let squad/league strength
#                             dominate the signal instead of managerial
#                             philosophy. Kept as "rate" only where no
#                             sensible ratio denominator exists in the
#                             available columns (documented per case below).
#   ("asis", col)           -- already a rate/percentage, used directly.
# invert: term names (as they appear in the built dataframe) where a LOWER
#         raw value means a HIGHER concept score (brief SS25 -- never
#         silently flip a sign without saying so).

CONCEPTS = {
    "progressive_passing": {
        "terms": [
            ("ratio", "passing__PrgP", "passing__Att_Total"),
            ("ratio", "passing__Final_Third", "passing__Att_Total"),
            ("ratio", "passing__PPA", "passing__Att_Total"),
            ("asis", "passing__Cmp_percent_Total"),
        ],
        "invert": [],
    },
    "progressive_carrying": {
        "terms": [
            ("ratio", "possession__PrgC_Carries", "possession__Carries_Carries"),
            ("ratio", "possession__Final_Third_Carries", "possession__Carries_Carries"),
            ("ratio", "possession__CPA_Carries", "possession__Carries_Carries"),
        ],
        "invert": [],
    },
    "possession_retention": {
        # Touches per-90 is kept as a raw rate deliberately: overall
        # involvement/volume IS part of what "retention-oriented" means
        # football-wise (a deep-lying playmaker touches the ball a lot), so
        # unlike the progression concepts there is no natural share
        # denominator that wouldn't just re-derive Cmp_percent_Total.
        "terms": [
            ("rate", "possession__Touches_Touches"),
            ("asis", "passing__Cmp_percent_Total"),
            ("asis", "possession__Succ_percent_Take_Ons"),
        ],
        "invert": [],
    },
    "chance_creation": {
        # summary__SCA_SCA / summary__GCA_SCA dropped: the 'summary' FBref
        # match-level block is only populated from Season_End_Year 2025
        # onward for EVERY league (confirmed by direct coverage audit, see
        # outputs/audit/data_availability_matrix.md SS5) -- entirely absent
        # for our whole 2017/18-2023/24 in-scope window. KP and xA (both
        # 'passing' block) are the only chance-creation terms actually
        # measurable in-window.
        "terms": [
            ("ratio", "passing__KP", "passing__Att_Total"),
            ("ratio", "passing__xA", "passing__Att_Total"),
        ],
        "invert": [],
    },
    "box_presence": {
        # summary__Sh / summary__SoT / summary__npxG_Expected dropped for the
        # same reason as chance_creation above -- no shooting-detail block
        # exists at match level for our window (a dedicated 'shooting'
        # release asset does not exist; shot data lives only in the
        # unavailable 'summary' block). Box presence in this iteration is
        # therefore box OCCUPATION only (touches in the penalty area, as a
        # share of total touches), not shot quality/finishing -- a real,
        # documented scope reduction, not a silent one.
        "terms": [
            ("ratio", "possession__Att Pen_Touches", "possession__Touches_Touches"),
        ],
        "invert": [],
    },
    "pressing_intensity": {
        # OD-5 closed: "padj_rate" terms multiply the per-90 rate by a
        # possession-adjustment factor (league-average opponent possession
        # share / this team's own opponent possession share -- see
        # attach_possession_adjustment() below) before z-scoring. A team that
        # dominates the ball faces less opponent-in-possession time and so
        # racks up fewer raw defensive actions for the same underlying
        # pressing INTENT; padj scales that back up to a like-for-like
        # opponent-possession basis. Requires a "_padj_factor" column to
        # already be present on the dataframe (attach_possession_adjustment);
        # falls back to an unadjusted "rate" (padj_factor defaults to 1.0)
        # wherever team possession data isn't available, so this degrades
        # gracefully rather than breaking.
        "terms": [
            ("padj_rate", "defense__Att 3rd_Tackles"),
            ("padj_rate", "defense__Mid 3rd_Tackles"),
            ("padj_rate", "defense__Tkl_Tackles"),
            ("padj_rate", "defense__Int"),
            ("padj_rate", "misc__Recov"),
        ],
        "invert": [],
    },
    "individual_defending": {
        "terms": [
            ("asis", "defense__Tkl_percent_Challenges"),
            ("ratio", "defense__Tkl+Int", "possession__Touches_Touches"),
        ],
        "invert": [],
    },
    "aerial_play": {
        "terms": [
            ("rate", "misc__Won_Aerial_Duels"),
            ("asis", "misc__Won_percent_Aerial_Duels"),
        ],
        "invert": [],
    },
    "crossing": {
        "terms": [
            ("ratio", "misc__Crs", "possession__Touches_Touches"),
            ("ratio", "passing__CrsPA", "passing__Att_Total"),
        ],
        "invert": [],
    },
    "goalkeeper_distribution": {
        # Our own manager research (manager_philosophy_hypotheses.md SS1.2,
        # SS3.2) names the goalkeeper-as-auxiliary-defender mechanism as one
        # of the clearest discriminators for Guardiola and De Zerbi
        # specifically -- and the data for it (FBref's 'keeper' /
        # 'keepers_adv' block) was sitting unused. All three terms describe
        # how much a goalkeeper favours long/launched distribution; every
        # term is inverted so a HIGH concept score means MORE build-up-
        # oriented (short distribution), consistent with the polarity of
        # progressive_passing/possession_retention, which this concept feeds
        # alongside in TD1. By construction this concept is NaN for every
        # outfield player (they have no 'keeper' block row) -- see
        # build_dimension_scores' NaN-aware weighting, which renormalises
        # TD1's weights over just the concepts available for a given player.
        "terms": [
            ("asis", "keeper__Cmp_percent_Launched"),  # share of launched (long) passes that are completed
            ("asis", "keeper__Launch_percent_Passes"),  # share of all passes that are launched (long)
            ("asis", "keeper__AvgLen_Passes"),  # average pass length in yards
        ],
        "invert": ["t0", "t1", "t2"],
    },
}

# Tactical dimensions (subset of football_ontology.md TD1-TD13 constructible
# from player-level per-90 features -- TD5/TD8/TD10/TD13 need team-level or
# opponent-relative context not yet built and are deferred, see module notes
# at the bottom of this file) -> {concept: weight}. Weights are explicit,
# argued football-knowledge judgements (OD-4), not fitted.
DIMENSION_WEIGHTS = {
    "TD1_buildup_directness": {"progressive_passing": 0.5, "possession_retention": 0.3, "goalkeeper_distribution": 0.2},
    "TD3_progression_passing": {"progressive_passing": 1.0},
    "TD4_progression_carrying": {"progressive_carrying": 1.0},
    "TD6_chance_creation": {"chance_creation": 0.7, "crossing": 0.3},
    "TD7_box_presence": {"box_presence": 1.0},
    "TD9_pressing_intensity": {"pressing_intensity": 1.0},
    "TD11_individual_defending": {"individual_defending": 0.7, "aerial_play": 0.3},
}


def _term_columns(term: tuple) -> list[str]:
    """Raw column names a term depends on -- term[1] for rate/padj_rate/asis,
    term[1:] (num, denom) for ratio."""
    return list(term[1:])


def compute_concept_terms(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Evaluate every concept's terms (rate / padj_rate / ratio / asis)
    against `df`.

    The SAME function is used for both the manager-sample dataframe and the
    full-league population dataframe in build_population_baseline, so the
    ratio/rate definitions are guaranteed identical in both places -- no risk
    of the baseline silently measuring something slightly different from
    what it is meant to standardise.
    """
    minutes = df["Min"].replace(0, np.nan) if "Min" in df.columns else None
    padj = df["_padj_factor"] if "_padj_factor" in df.columns else 1.0
    out: dict[str, pd.DataFrame] = {}
    for name, spec in CONCEPTS.items():
        cols = {}
        for i, term in enumerate(spec["terms"]):
            key = f"t{i}"
            if term[0] == "rate":
                col = term[1]
                # No fillna(0) on the raw column: a block that FBref never
                # published for this league/season (e.g. Serie A 'passing'
                # before 2023/24) is NaN for every row, and must stay NaN --
                # not be silently treated as "the player did zero of this
                # action" (see outputs/results/task4_evaluation_findings.md).
                # A genuine recorded zero (player played and did 0 tackles,
                # say) is already stored as 0 in the source data, not NaN.
                cols[key] = df[col] * 90 / minutes if col in df.columns else np.nan
            elif term[0] == "padj_rate":
                # Possession-adjusted rate (OD-5): raw_per90 * padj_factor,
                # where padj_factor = league_avg_opponent_poss / this team's
                # own opponent_poss (see attach_possession_adjustment). A team
                # whose opponents had LESS of the ball (this team dominated
                # possession) gets scaled UP, since it had fewer opportunities
                # to rack up defensive actions for the same underlying intent.
                # padj_factor defaults to 1.0 (no adjustment) if the column
                # wasn't attached -- degrades to a plain "rate", not an error.
                col = term[1]
                cols[key] = (df[col] * 90 / minutes * padj) if col in df.columns else np.nan
            elif term[0] == "ratio":
                num, denom = term[1], term[2]
                if num in df.columns and denom in df.columns:
                    cols[key] = df[num] / df[denom].replace(0, np.nan)
                else:
                    cols[key] = np.nan
            elif term[0] == "asis":
                col = term[1]
                cols[key] = df[col] if col in df.columns else np.nan
        combined = pd.DataFrame(cols, index=df.index)
        for inv_key in spec.get("invert", []):
            if inv_key in combined.columns:
                combined[inv_key] = -combined[inv_key]
        out[name] = combined
    return out


# --------------------------------------------------------------------------
# 2a. Possession adjustment (closes OD-5, see pressing_intensity above)
# --------------------------------------------------------------------------

_TEAM_POSSESSION_PATH = None  # resolved lazily to avoid a hard import-time dependency on data_sources


def _team_possession_table() -> pd.DataFrame:
    global _TEAM_POSSESSION_PATH
    if _TEAM_POSSESSION_PATH is None:
        from data_sources import PROJECT_ROOT
        _TEAM_POSSESSION_PATH = PROJECT_ROOT / "data" / "raw" / "fbref_season" / "team_possession.parquet"
    df = pd.read_parquet(_TEAM_POSSESSION_PATH)
    opp = df[df.Team_or_Opponent == "opponent"][["Squad", "Comp", "Season_End_Year", "Poss"]].rename(columns={"Poss": "opp_poss"})
    league_avg = opp.groupby(["Comp", "Season_End_Year"])["opp_poss"].mean().rename("league_avg_opp_poss").reset_index()
    return opp.merge(league_avg, on=["Comp", "Season_End_Year"])


# FBref season-level 'Squad' spelling differs from some match-level 'team'
# strings used elsewhere in this project (manager_attribution.MANAGER_WINDOWS).
_TEAM_NAME_ALIASES = {"Brighton & Hove Albion": "Brighton"}
_LEAGUE_CODE_TO_COMP = {"ENG": "Premier League", "ESP": "La Liga", "ITA": "Serie A", "GER": "Bundesliga", "FRA": "Ligue 1"}


def attach_possession_adjustment(
    df: pd.DataFrame, team_col: str, comp_col: str | None = None, league_code_col: str | None = None,
    season_col: str = "Season_End_Year",
) -> pd.DataFrame:
    """Joins a `_padj_factor` column onto `df` (see compute_concept_terms's
    "padj_rate" term type). Provide either `comp_col` (season-level data,
    where the competition name is already present as e.g. "Serie A") or
    `league_code_col` (match-level data, where only a 2-3 letter code like
    "ITA" is present -- mapped via _LEAGUE_CODE_TO_COMP).

    Rows for teams/seasons not found in the team-possession table (e.g. a
    club outside the big-5 leagues, or a season this table doesn't cover)
    get padj_factor = 1.0 -- i.e. no adjustment, not a dropped row.
    """
    df = df.copy()
    team_norm = df[team_col].replace(_TEAM_NAME_ALIASES)
    if comp_col is not None:
        comp = df[comp_col]
    else:
        comp = df[league_code_col].map(_LEAGUE_CODE_TO_COMP)

    lookup = _team_possession_table()
    key = pd.DataFrame({"Squad": team_norm, "Comp": comp, "Season_End_Year": df[season_col]})
    merged = key.merge(lookup, on=["Squad", "Comp", "Season_End_Year"], how="left")
    padj_factor = merged["league_avg_opp_poss"] / merged["opp_poss"]
    df["_padj_factor"] = padj_factor.fillna(1.0).to_numpy()
    return df


# --------------------------------------------------------------------------
# 2b. League-wide population baseline for z-scoring
# --------------------------------------------------------------------------
# Z-scoring concept terms against only the 4-6 clubs in our manager sample
# would conflate managerial philosophy with squad quality (exactly the
# team-strength / team-weakness confounds flagged in
# outputs/football_knowledge/manager_philosophy_hypotheses.md SS4.4). Instead,
# every concept term is standardised against the full big-5-league
# population (ENG/ITA/FRA, all ~30 teams each, 2017/18-2023/24) in the same
# position group -- so a "high" score means genuinely unusual for the
# position across the league, not merely above-average for this project's
# 4-6 clubs.

def _needed_raw_columns() -> dict[str, set[str]]:
    needed: dict[str, set[str]] = {}
    for spec in CONCEPTS.values():
        for term in spec["terms"]:
            for prefixed_col in _term_columns(term):
                stat_type, raw_col = prefixed_col.split("__", 1)
                needed.setdefault(stat_type, set()).add(raw_col)
    return needed


def build_population_baseline(
    leagues: tuple[str, ...] = ("ENG", "ITA", "FRA"),
    season_range: tuple[int, int] = (2018, 2024),
) -> pd.DataFrame:
    """Per-term, position-group mean/std, computed from the FULL league
    population (not just the manager-attributed subset). Returns a long
    dataframe: columns = [concept, term, pos_group, mean, std, n].
    """
    from data_sources import FBREF_DIR
    from manager_attribution import MERGE_KEYS

    needed = _needed_raw_columns()
    stat_types = sorted(needed)

    baseline_rows = []
    for league in leagues:
        merged = None
        for stat_type in stat_types:
            path = FBREF_DIR / f"{league}_{stat_type}_player.csv"
            raw_cols = sorted(needed[stat_type])
            extra = {"Pos", "Min"} if merged is None else set()
            usecols_set = set(MERGE_KEYS) | extra | set(raw_cols)
            df = pd.read_csv(path, usecols=lambda c: c in usecols_set, low_memory=False)
            df = df[df.Season_End_Year.between(*season_range)]
            prefix = f"{stat_type}__"
            rename_cols = {c: f"{prefix}{c}" for c in raw_cols if c in df.columns}
            df = df.rename(columns=rename_cols)
            if merged is None:
                merged = df
            else:
                keep = MERGE_KEYS + [f"{prefix}{c}" for c in raw_cols if f"{prefix}{c}" in df.columns]
                merged = merged.merge(df[keep], on=MERGE_KEYS, how="outer")

        merged["_league_code"] = league
        merged = attach_possession_adjustment(merged, team_col="Team", league_code_col="_league_code")
        merged["pos_group"] = position_group(merged)
        terms_by_concept = compute_concept_terms(merged)
        for concept, term_df in terms_by_concept.items():
            for term_key in term_df.columns:
                vals = term_df[term_key]
                stats = vals.groupby(merged["pos_group"]).agg(["mean", "std", "count"])
                for pos_grp, r in stats.iterrows():
                    baseline_rows.append({
                        "concept": concept, "term": term_key, "pos_group": pos_grp,
                        "mean": r["mean"], "std": r["std"], "n": r["count"], "league": league,
                    })

    long_df = pd.DataFrame(baseline_rows)

    def pool(g):
        # Some (concept, term, league) cells have n=0 / NaN mean/std -- e.g.
        # a league whose relevant FBref block wasn't published at all inside
        # `season_range` for that specific column (this happened for ITA's
        # 'Att Pen_Touches', which -- unlike the rest of the possession
        # block -- didn't start populating until 2025, one season later than
        # everything else in that block; see decision_log.md D-006). Those
        # cells must be dropped before pooling, not left in: np.average does
        # not skip NaN, so a single NaN entry -- even with weight 0 -- would
        # silently poison the whole pooled statistic to NaN.
        valid = g[g["n"] > 0]
        if valid.empty:
            return pd.Series({"mean": np.nan, "std": np.nan, "n": 0})
        n = valid["n"]
        mean = np.average(valid["mean"], weights=n)
        var = np.average(valid["std"] ** 2 + (valid["mean"] - mean) ** 2, weights=n)
        return pd.Series({"mean": mean, "std": np.sqrt(var), "n": n.sum()})

    pooled = long_df.groupby(["concept", "term", "pos_group"]).apply(pool, include_groups=False).reset_index()
    return pooled


def build_concept_scores(
    player_match: pd.DataFrame,
    population_baseline: pd.DataFrame | None = None,
) -> tuple[pd.DataFrame, dict]:
    """Concept terms -> position-z-scored concept scores.

    Returns (concept_df, pca_diagnostics). concept_df has one row per
    player-match, columns = concept names, values = position-group z-scores
    (mean of the concept's standardised terms). pca_diagnostics reports, per
    concept, the variance explained by the first PC of its terms -- the
    OD-4 statistical-coherence check: a concept whose terms don't share a
    dominant first component is a hand-grouping the data does not support.
    """
    df = player_match.copy()
    df["pos_group"] = position_group(df)

    concept_inputs = compute_concept_terms(df)

    pca_diagnostics = {}
    concept_scores = pd.DataFrame(index=df.index)
    for name, inputs in concept_inputs.items():
        valid = inputs.replace([np.inf, -np.inf], np.nan).dropna()
        if len(valid) < 30 or inputs.shape[1] < 2:
            pca_diagnostics[name] = {"n_inputs": inputs.shape[1], "variance_explained_pc1": None}
        else:
            scaled = StandardScaler().fit_transform(valid)
            pca = PCA(n_components=1).fit(scaled)
            pca_diagnostics[name] = {
                "n_inputs": inputs.shape[1],
                "variance_explained_pc1": round(float(pca.explained_variance_ratio_[0]), 3),
            }

        z_parts = []
        for col in inputs.columns:
            series = inputs[col].replace([np.inf, -np.inf], np.nan)
            if population_baseline is not None:
                base = population_baseline[
                    (population_baseline.concept == name) & (population_baseline.term == col)
                ].set_index("pos_group")
                if len(base):
                    grp_mean = df["pos_group"].map(base["mean"])
                    grp_std = df["pos_group"].map(base["std"]).replace(0, np.nan)
                else:
                    grp_mean = series.groupby(df["pos_group"]).transform("mean")
                    grp_std = series.groupby(df["pos_group"]).transform("std").replace(0, np.nan)
            else:
                grp_mean = series.groupby(df["pos_group"]).transform("mean")
                grp_std = series.groupby(df["pos_group"]).transform("std").replace(0, np.nan)
            z_parts.append((series - grp_mean) / grp_std)
        concept_scores[name] = pd.concat(z_parts, axis=1).mean(axis=1)

    return concept_scores, pca_diagnostics


def build_dimension_scores(concept_scores: pd.DataFrame) -> pd.DataFrame:
    """Concept scores -> tactical dimension scores, via the explicit weights
    in DIMENSION_WEIGHTS. NaN-aware PER ROW: a dimension with a concept that
    is unavailable for a given player (e.g. `goalkeeper_distribution` is
    NaN for every outfield player, by construction) is computed from
    whichever of its concepts ARE available for that row, with weights
    renormalised over just those -- not silently propagated to NaN for the
    whole dimension. A row where every one of a dimension's concepts is
    missing still correctly yields NaN for that dimension."""
    dims = pd.DataFrame(index=concept_scores.index)
    for dim, weights in DIMENSION_WEIGHTS.items():
        cols = list(weights.keys())
        w = np.array([weights[c] for c in cols])
        vals = concept_scores[cols].to_numpy(dtype=float)
        mask = ~np.isnan(vals)
        w_applied = mask * w  # zero out the weight of any missing concept, per row
        w_sum = w_applied.sum(axis=1)
        with np.errstate(invalid="ignore", divide="ignore"):
            weighted = np.nansum(vals * w_applied, axis=1) / w_sum
        weighted[w_sum == 0] = np.nan
        dims[dim] = weighted
    return dims


def _nan_aware_wmean(group: pd.DataFrame, value_cols: list[str], weight_col: str) -> pd.Series:
    """Weighted mean per column that SKIPS rows where that column is NaN,
    rather than treating missing data as zero. Some concepts (progression,
    possession, chance creation, box presence, crossing) are entirely
    unmeasurable for Sassuolo/Benevento pre-2024 -- the 'passing',
    'passing_types', 'possession' and 'keeper' FBref match-level blocks are
    only populated for Serie A/Ligue 1 from 2023/24 onward (confirmed by
    direct coverage audit, outputs/audit/data_availability_matrix.md SS5).
    Filling that with 0 would silently misrepresent "no data" as "exactly
    league average", which is precisely the bug this function fixes -- see
    outputs/results/task4_evaluation_findings.md for the full account."""
    w = group[weight_col]
    out = {}
    for c in value_cols:
        vals = group[c]
        mask = vals.notna()
        out[c] = np.average(vals[mask], weights=w[mask]) if mask.any() else np.nan
    return pd.Series(out)


def build_player_profiles(player_match: pd.DataFrame, concept_scores: pd.DataFrame, dim_scores: pd.DataFrame) -> pd.DataFrame:
    """Aggregate match-level dimension scores to one profile per
    (player, manager, team, Season_End_Year) -- minutes-weighted mean, so a
    5-minute cameo doesn't count as heavily as a full match. NaN-aware: see
    _nan_aware_wmean."""
    keys = ["Player", "Player_Href", "manager", "team", "Season_End_Year", "Pos"]
    weights = player_match["Min"].clip(lower=1)
    combined = pd.concat([player_match[keys], concept_scores, dim_scores], axis=1)
    combined["_w"] = weights

    value_cols = list(concept_scores.columns) + list(dim_scores.columns)
    profiles = combined.groupby(keys, dropna=False).apply(
        lambda g: _nan_aware_wmean(g, value_cols, "_w"), include_groups=False
    ).reset_index()
    minutes_total = player_match.groupby(keys, dropna=False)["Min"].sum().reset_index(name="total_minutes")
    profiles = profiles.merge(minutes_total, on=keys)
    return profiles


def build_manager_profiles(player_profiles: pd.DataFrame, dim_cols: list[str]) -> pd.DataFrame:
    """Manager profile = minutes-weighted mean of every player-manager-season
    dimension score under that manager, per brief SS10-11 -- i.e. built from
    the players' measured behaviour under the manager, not a hand-picked
    label. NaN-aware: a manager whose sample partly lacks data for a
    dimension (e.g. De Zerbi's Sassuolo/Benevento seasons for the
    progression/possession dimensions) is averaged only over the players
    and seasons where that dimension is actually measurable."""
    return player_profiles.groupby("manager").apply(
        lambda g: _nan_aware_wmean(g, dim_cols, "total_minutes"), include_groups=False
    ).reset_index()


def build_club_within_manager_profiles(player_profiles: pd.DataFrame, dim_cols: list[str]) -> pd.DataFrame:
    """Per (manager, club) centroid -- the club-identity-bias check (brief
    SS18-19). Only De Zerbi has more than one in-scope club; comparing his
    club-level centroids to each other and to Guardiola's/Klopp's single-club
    centroids tests whether the model captures something that survives a
    change of squad, league and teammates, or whether it is really just
    learning club identity. NaN-aware, see _nan_aware_wmean -- clubs/seasons
    with no data for a dimension surface as NaN here, not a misleading 0."""
    return player_profiles.groupby(["manager", "team"]).apply(
        lambda g: _nan_aware_wmean(g, dim_cols, "total_minutes"), include_groups=False
    ).reset_index()
