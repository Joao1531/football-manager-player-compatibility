"""
Season-level FBref data integration.

Discovery (2026-08-11, after the match-level pipeline was already built and
evaluated): FBref's SEASON-level aggregated tables (the `fb_big5_advanced_season_stats`
release) have FULL coverage 2017/18-2022/23 across all five big-5 leagues --
including Serie A and Ligue 1, where the MATCH-level tables (used in
notebooks 02-04) are entirely unpopulated before 2023/24 (decision_log.md
D-006). This closes most of the De Zerbi/Sassuolo data gap: Sassuolo's whole
three-season tenure (2018/19-2020/21) is a SAFE, whole-season attribution
(no mid-season manager change, per manager_tenures.csv row D5) and can now
be sourced from season-level data instead of contributing nothing.

This module also unlocks a genuine feature upgrade: the season-level
'defense' block still carries the original StatsBomb-sourced `Press_Pressures`
column (a direct pressing-actions count) for seasons through 2021/22 -- FBref
switched to Opta in late Oct 2022, so 2022/23 (Season_End_Year 2023) onward
lacks it, matching the match-level pipeline's own provider-switch finding
(decision_log.md D-003). Where available, this is a strictly better pressing
signal than the match-level pipeline's tackle-location proxy (pressing was
the ONE dimension that carried real discriminating signal in the match-level
evaluation, per outputs/results/task4_evaluation_findings.md SS6b) -- so it
is added as an additional, gracefully-degrading term on pressing_intensity,
never a replacement for the existing terms.

Season-level rows are used for:
1. SAFE, whole-season manager tenure rows (Sassuolo all 3 seasons; Man
   City/Liverpool 2017/18-2021/22, where season-level coverage reaches --
   their 2022/23 and 2023/24 seasons still use the match-level pipeline,
   which already has no gap for ENG).
2. The full multi-league PLAYER UNIVERSE for the app's player browser
   (every player in the big-5 leagues, 2017/18-2022/23) -- this is NOT
   restricted to the three in-scope managers' clubs.

Season-level rows are NOT used for mid-season-split attribution (Benevento,
Brighton 2022/23, Marseille 2025/26) -- a season aggregate cannot be split
by match date, so those rows still come exclusively from the match-level
pipeline (notebooks 02-04), or are excluded where neither source has the
needed granularity (Benevento, unchanged from before).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from football_features import CONCEPTS, DIMENSION_WEIGHTS, position_group, attach_possession_adjustment
from data_sources import PROJECT_ROOT

SEASON_DIR = PROJECT_ROOT / "data" / "raw" / "fbref_season"

SEASON_BLOCKS = ["passing", "possession", "defense", "misc", "standard", "shooting", "keepers_adv"]

# Season-level metadata columns shared across every block (after the
# column-rename step already applied when converting .rds -> .parquet, see
# the one-off conversion script; kept here as the merge/exclusion key set).
SEASON_METADATA_COLS = {
    "Season_End_Year", "Squad", "Comp", "Player", "Nation", "Pos", "Age", "Born",
    "Mins_Per_90", "MP_Playing", "Starts_Playing", "Min_Playing", "Mins_Per_90_Playing", "Url",
}

SEASON_MERGE_KEYS = ["Player", "Squad", "Comp", "Season_End_Year"]

# Extra pressing_intensity terms available only in season-level data
# (StatsBomb-sourced 'Pressures', 2017/18-2021/22 only -- see module
# docstring). Added to CONCEPTS in-place so both the match-level and
# season-level pipelines share one concept/dimension definition, per the
# project's existing rule against maintaining two divergent copies of a
# feature definition.
_SEASON_PRESSING_TERMS = [
    ("padj_rate", "defense__Press_Pressures"),
    ("padj_rate", "defense__Att 3rd_Pressures"),
    ("padj_rate", "defense__Mid 3rd_Pressures"),
]
for _t in _SEASON_PRESSING_TERMS:
    if _t not in CONCEPTS["pressing_intensity"]["terms"]:
        CONCEPTS["pressing_intensity"]["terms"].append(_t)


def load_season_block(name: str) -> pd.DataFrame:
    return pd.read_parquet(SEASON_DIR / f"{name}.parquet")


def build_season_league_dataset(
    leagues: tuple[str, ...] = ("Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"),
) -> pd.DataFrame:
    """Merge all season-level stat blocks into one player x team x season
    dataframe, column-prefixed exactly like the match-level pipeline
    (`stat_block__RawColumn`) so `football_features.compute_concept_terms`
    works unchanged on the result.
    """
    merged = None
    for block in SEASON_BLOCKS:
        df = load_season_block(block)
        df = df[df.Comp.isin(leagues)]
        new_cols = [c for c in df.columns if c not in SEASON_METADATA_COLS and c not in SEASON_MERGE_KEYS]
        # Season-level's goalkeeper block is named 'keepers_adv'; match-level's
        # equivalent block is named 'keeper'. Use the match-level prefix so
        # CONCEPTS' column references (e.g. "keeper__AvgLen_Passes") resolve
        # against both sources without maintaining two parallel definitions.
        prefix = "keeper__" if block == "keepers_adv" else f"{block}__"
        df = df.rename(columns={c: f"{prefix}{c}" for c in new_cols})
        keep_meta = SEASON_MERGE_KEYS + (["Pos", "Mins_Per_90"] if merged is None else [])
        keep = keep_meta + [c for c in df.columns if c.startswith(prefix)]
        keep = [c for c in keep if c in df.columns]
        df = df[keep]
        if merged is None:
            merged = df
        else:
            merged = merged.merge(df, on=SEASON_MERGE_KEYS, how="outer")

    # Reconstruct a 'Min' column (total minutes) from Mins_Per_90, matching
    # the match-level pipeline's rate-calc convention (raw_count * 90 / Min).
    merged["Min"] = merged["Mins_Per_90"] * 90
    merged["Player_Href"] = merged.get("Url", pd.Series(index=merged.index, dtype=object))
    merged = attach_possession_adjustment(merged, team_col="Squad", comp_col="Comp")
    return merged


SAFE_SEASON_TENURES = [
    # manager, Squad (FBref season-level name), Comp, season_end_years covered
    ("Pep Guardiola", "Manchester City", "Premier League", list(range(2018, 2023))),
    ("Jürgen Klopp", "Liverpool", "Premier League", list(range(2018, 2023))),
    ("Roberto De Zerbi", "Sassuolo", "Serie A", [2019, 2020, 2021]),
]


def build_season_population_baseline(season_df: pd.DataFrame) -> pd.DataFrame:
    """Position-group mean/std per concept term, computed from the full
    season-level player universe (all big-5 clubs, 2017/18-2022/23) --
    the season-level equivalent of football_features.build_population_baseline,
    kept as a separate function because the underlying population (season
    aggregates vs per-match rows) is a different statistical object, even
    though the CONCEPTS definitions are shared.
    """
    from football_features import compute_concept_terms

    df = season_df.copy()
    df["pos_group"] = position_group(df)
    terms_by_concept = compute_concept_terms(df)

    rows = []
    for concept, term_df in terms_by_concept.items():
        for term_key in term_df.columns:
            vals = term_df[term_key].replace([np.inf, -np.inf], np.nan)
            stats = vals.groupby(df["pos_group"]).agg(["mean", "std", "count"])
            for pos_grp, r in stats.iterrows():
                rows.append({"concept": concept, "term": term_key, "pos_group": pos_grp,
                             "mean": r["mean"], "std": r["std"], "n": r["count"]})
    return pd.DataFrame(rows)


def build_manager_season_rows(season_df: pd.DataFrame) -> pd.DataFrame:
    """Extract the SAFE, whole-season manager-attributed rows from the full
    season-level league dataset (see SAFE_SEASON_TENURES)."""
    frames = []
    for manager, squad, comp, years in SAFE_SEASON_TENURES:
        sub = season_df[(season_df.Squad == squad) & (season_df.Comp == comp) & (season_df.Season_End_Year.isin(years))].copy()
        sub["manager"] = manager
        sub["team"] = squad
        sub["source"] = "season_level"
        frames.append(sub)
    return pd.concat(frames, ignore_index=True)
