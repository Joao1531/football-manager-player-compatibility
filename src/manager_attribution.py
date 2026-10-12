"""
Match-level manager attribution and dataset assembly.

Implements the project's non-negotiable data-integrity rule: a player-match
observation may only be attributed to a manager for the exact window that
manager was in charge of that team (project brief SS12-15). Season-level
joins are unsafe wherever a manager changed mid-season -- see
data/external/manager_tenures.md for the verified, sourced tenure research
this module encodes.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from data_sources import (
    DATA_PROCESSED,
    FBREF_KEYS,
    FBREF_STAT_TYPES,
    load_fbref,
)

# --------------------------------------------------------------------------
# Manager attribution windows -- the in-scope quantitative sample
# --------------------------------------------------------------------------
# Each row is [start, end) on Match_Date. Boundaries are the tighter of
# (a) the verified tenure window in data/external/manager_tenures.csv and
# (b) the open-data availability window confirmed in
# outputs/audit/data_availability_matrix.md. Where the tenure table's
# first_match_date lacks day precision (month only), the tenure row's
# appointed_date is used as a conservative lower bound instead, since in
# every such case the in-scope season starts well after the appointment
# date anyway (see decision_log.md D-004).

MANAGER_WINDOWS = [
    # manager, team (FBref name), start (inclusive), end (exclusive), tenure_row, confidence
    ("Pep Guardiola", "Manchester City", "2017-07-01", "2024-07-01", "G4", "high"),
    ("Jürgen Klopp", "Liverpool", "2017-07-01", "2024-07-01", "K3", "high"),
    ("Roberto De Zerbi", "Sassuolo", "2018-07-01", "2021-07-01", "D5", "high"),
    ("Roberto De Zerbi", "Benevento", "2017-10-23", "2018-07-01", "D4", "low"),
    ("Roberto De Zerbi", "Brighton & Hove Albion", "2022-10-01", "2024-07-01", "D7", "high"),
    ("Roberto De Zerbi", "Marseille", "2024-07-01", "2026-02-09", "D8", "high"),
]

MANAGER_WINDOWS_DF = pd.DataFrame(
    MANAGER_WINDOWS,
    columns=["manager", "team", "window_start", "window_end", "tenure_row", "confidence"],
).assign(
    window_start=lambda d: pd.to_datetime(d.window_start),
    window_end=lambda d: pd.to_datetime(d.window_end),
)

TEAM_TO_LEAGUE = {
    "Manchester City": "ENG",
    "Liverpool": "ENG",
    "Brighton & Hove Albion": "ENG",
    "Sassuolo": "ITA",
    "Benevento": "ITA",
    "Marseille": "FRA",
}

# Metadata columns repeated identically across every FBref match-level stat
# block (confirmed by direct header inspection of the raw CSVs). Anything
# not in this set is a stat-block-specific football metric and gets
# prefixed with the stat-block name on merge to avoid silent collisions
# (e.g. 'Int' and 'TklW' are both published in the defense AND misc blocks).
FBREF_METADATA_COLS = {
    "MatchURL", "League", "Match_Date", "Matchweek", "Home_Team", "Home_Formation",
    "Home_Score", "Home_xG", "Home_Goals", "Home_Yellow_Cards", "Home_Red_Cards",
    "Away_Team", "Away_Formation", "Away_Score", "Away_xG", "Away_Goals",
    "Away_Yellow_Cards", "Away_Red_Cards", "Game_URL", "Team", "Home_Away",
    "Player", "Player_Href", "Player_Num", "Nation", "Pos", "Age", "Min",
    "Competition_Name", "Gender", "Country", "Tier", "Season_End_Year",
    "league_code",
}

MERGE_KEYS = ["MatchURL", "Player", "Team", "Season_End_Year"]


def load_tenure_table() -> pd.DataFrame:
    path = Path(__file__).resolve().parents[1] / "data" / "external" / "manager_tenures.csv"
    df = pd.read_csv(path)
    for col in ("announced_date", "appointed_date", "first_match_date", "last_match_date", "departure_date"):
        df[col + "_parsed"] = pd.to_datetime(df[col], errors="coerce", format="mixed")
    return df


def build_player_match_dataset(
    stat_types: list[str] | None = None,
) -> pd.DataFrame:
    """Assemble the manager-attributed player x match dataset.

    For every (manager, team, window) row in MANAGER_WINDOWS, filters the
    relevant league's FBref match-level files down to that team and date
    window, merges the requested stat blocks on MERGE_KEYS, and stamps the
    manager label. Rows outside every window (i.e. matches under a
    different manager) are never included -- this function only ever
    returns manager-attributed rows, by construction.
    """
    stat_types = stat_types or FBREF_STAT_TYPES
    frames = []

    for manager, team, start, end, tenure_row, confidence in MANAGER_WINDOWS:
        league = TEAM_TO_LEAGUE[team]
        merged = None
        for st in stat_types:
            df = load_fbref(league, st)
            df = df[(df.Team == team) & (df.Match_Date >= start) & (df.Match_Date < end)].copy()
            if df.empty:
                continue
            new_cols = [c for c in df.columns if c not in FBREF_METADATA_COLS and c not in MERGE_KEYS]
            prefix = f"{st}__"
            df = df.rename(columns={c: f"{prefix}{c}" for c in new_cols})
            if merged is None:
                merged = df
            else:
                keep_cols = MERGE_KEYS + [c for c in df.columns if c.startswith(prefix)]
                merged = merged.merge(df[keep_cols], on=MERGE_KEYS, how="outer")
        if merged is None or merged.empty:
            continue
        merged["manager"] = manager
        merged["team"] = team
        merged["tenure_row"] = tenure_row
        merged["attribution_confidence"] = confidence
        merged["window_start"] = start
        merged["window_end"] = end
        frames.append(merged)

    out = pd.concat(frames, ignore_index=True)
    return out


def integrity_audit(player_match: pd.DataFrame) -> pd.DataFrame:
    """Per brief SS49: a manager x team x season summary table for review
    before any modelling proceeds. Flags anything that looks wrong.
    """
    g = (
        player_match.groupby(["manager", "team", "Season_End_Year", "tenure_row", "attribution_confidence"])
        .agg(
            matches=("MatchURL", "nunique"),
            players=("Player", "nunique"),
            player_match_rows=("MatchURL", "size"),
            total_minutes=("Min", "sum"),
            earliest_match=("Match_Date", "min"),
            latest_match=("Match_Date", "max"),
        )
        .reset_index()
        .sort_values(["manager", "team", "Season_End_Year"])
    )

    # Checks: duplicate (MatchURL, Player) rows within one manager-team-season
    dupe_mask = player_match.duplicated(subset=["MatchURL", "Player", "Team"], keep=False)
    g["duplicate_rows_flag"] = g.apply(
        lambda r: bool(
            dupe_mask[
                (player_match.manager == r.manager)
                & (player_match.team == r.team)
                & (player_match.Season_End_Year == r.Season_End_Year)
            ].any()
        ),
        axis=1,
    )
    # Window-bounds check: every row's Match_Date must fall inside its stamped window
    oob = player_match[
        (player_match.Match_Date < pd.to_datetime(player_match.window_start))
        | (player_match.Match_Date >= pd.to_datetime(player_match.window_end))
    ]
    g["rows_outside_window"] = g.apply(
        lambda r: int(
            (
                (oob.manager == r.manager) & (oob.team == r.team) & (oob.Season_End_Year == r.Season_End_Year)
            ).sum()
        ),
        axis=1,
    )
    return g


def save_processed(player_match: pd.DataFrame, name: str = "player_match_manager") -> Path:
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    path = DATA_PROCESSED / f"{name}.parquet"
    player_match.to_parquet(path, index=False)
    return path
