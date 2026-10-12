"""
Data source access layer.

Two public football data sources are used in this project. They are kept
strictly separate because their event definitions are not interchangeable
(see decision_log.md, D-003).

SOURCE A -- FBref match-level advanced player statistics (Opta-provided),
            mirrored as flat CSV release assets in the public
            `worldfootballR_data` repository. Primary modelling source.
            Unit of analysis: player x match.

SOURCE B -- StatsBomb Open Data (raw event data + match metadata that
            includes the manager in charge of each team in each match).
            Used for the event-level illustration of the raw-events ->
            football-concepts pipeline and as an independent
            cross-source validation set.
            Unit of analysis: event.

Both sources are free/open. Nothing here requires credentials.
"""

from __future__ import annotations

import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_EXTERNAL = PROJECT_ROOT / "data" / "external"
DATA_INTERIM = PROJECT_ROOT / "data" / "interim"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
OUTPUTS = PROJECT_ROOT / "outputs"

FBREF_DIR = DATA_RAW / "fbref_match"
SB_MANIFEST_DIR = DATA_RAW / "statsbomb_manifests"

# --------------------------------------------------------------------------
# SOURCE A -- FBref match-level advanced stats
# --------------------------------------------------------------------------

FBREF_RELEASE = (
    "https://github.com/JaseZiv/worldfootballR_data/releases/download/"
    "fb_advanced_match_stats"
)

# Leagues relevant to the three managers. USA is available but unused.
FBREF_LEAGUES = {
    "ENG": "Premier League",
    "ESP": "La Liga",
    "ITA": "Serie A",
    "GER": "Bundesliga",
    "FRA": "Ligue 1",
}

# Stat blocks published per league. Each is one CSV, player x match.
FBREF_STAT_TYPES = [
    "summary",
    "passing",
    "passing_types",
    "possession",
    "defense",
    "misc",
    "keeper",
]

# Columns identifying a single player-match observation across every block.
FBREF_KEYS = ["MatchURL", "Match_Date", "Team", "Player", "Season_End_Year"]


def fbref_url(league: str, stat_type: str, unit: str = "player") -> str:
    """URL of one FBref match-level CSV release asset."""
    return (
        f"{FBREF_RELEASE}/{league}_M_1st_{stat_type}_{unit}"
        f"_advanced_match_stats.csv"
    )


def fbref_local_path(league: str, stat_type: str, unit: str = "player") -> Path:
    return FBREF_DIR / f"{league}_{stat_type}_{unit}.csv"


def download_fbref(
    leagues: list[str] | None = None,
    stat_types: list[str] | None = None,
    unit: str = "player",
    force: bool = False,
    max_workers: int = 4,
) -> pd.DataFrame:
    """Download FBref match-level CSVs into data/raw/fbref_match/.

    Returns a manifest of what was fetched. Files are cached on disk; an
    existing non-trivial file is not re-downloaded unless force=True.
    """
    leagues = leagues or list(FBREF_LEAGUES)
    stat_types = stat_types or FBREF_STAT_TYPES
    FBREF_DIR.mkdir(parents=True, exist_ok=True)

    jobs = [(lg, st) for lg in leagues for st in stat_types]

    def _get(job):
        lg, st = job
        dest = fbref_local_path(lg, st, unit)
        if dest.exists() and dest.stat().st_size > 10_000 and not force:
            return {"league": lg, "stat_type": st, "status": "cached",
                    "mb": round(dest.stat().st_size / 1e6, 2)}
        try:
            urllib.request.urlretrieve(fbref_url(lg, st, unit), dest)
            return {"league": lg, "stat_type": st, "status": "downloaded",
                    "mb": round(dest.stat().st_size / 1e6, 2)}
        except Exception as exc:  # noqa: BLE001 - surfaced in the manifest
            return {"league": lg, "stat_type": st,
                    "status": f"ERROR: {type(exc).__name__}", "mb": 0.0}

    with ThreadPoolExecutor(max_workers) as pool:
        rows = list(pool.map(_get, jobs))
    return pd.DataFrame(rows)


def load_fbref(
    league: str, stat_type: str, unit: str = "player", **kwargs
) -> pd.DataFrame:
    """Load one cached FBref match-level CSV."""
    path = fbref_local_path(league, stat_type, unit)
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Run download_fbref(['{league}'], ['{stat_type}'])."
        )
    df = pd.read_csv(path, low_memory=False, **kwargs)
    df["Match_Date"] = pd.to_datetime(df["Match_Date"], errors="coerce")
    df["league_code"] = league
    return df


# --------------------------------------------------------------------------
# SOURCE B -- StatsBomb Open Data
# --------------------------------------------------------------------------

SB_BASE = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"


def sb_competitions(refresh: bool = False) -> pd.DataFrame:
    """The StatsBomb Open Data competition/season manifest."""
    SB_MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    path = SB_MANIFEST_DIR / "sb_competitions.json"
    if refresh or not path.exists():
        urllib.request.urlretrieve(f"{SB_BASE}/competitions.json", path)
    return pd.DataFrame(json.loads(path.read_text()))


def download_sb_matches(refresh: bool = False, max_workers: int = 8) -> int:
    """Cache every match manifest referenced by the competition manifest."""
    comps = sb_competitions(refresh=refresh)
    pairs = sorted(set(zip(comps.competition_id, comps.season_id)))
    SB_MANIFEST_DIR.mkdir(parents=True, exist_ok=True)

    def _get(pair):
        ci, si = pair
        dest = SB_MANIFEST_DIR / f"{ci}_{si}.json"
        if dest.exists() and dest.stat().st_size > 200 and not refresh:
            return True
        try:
            urllib.request.urlretrieve(f"{SB_BASE}/matches/{ci}/{si}.json", dest)
            return True
        except Exception:  # noqa: BLE001
            return False

    with ThreadPoolExecutor(max_workers) as pool:
        return sum(pool.map(_get, pairs))


def sb_match_manager_index() -> pd.DataFrame:
    """Flatten cached StatsBomb match manifests to one row per team-match.

    StatsBomb records the manager in charge of each team for each match,
    which gives match-level manager attribution directly from the data
    provider rather than from an external tenure lookup.
    """
    rows: list[dict] = []
    for path in sorted(SB_MANIFEST_DIR.glob("*.json")):
        if path.name == "sb_competitions.json":
            continue
        try:
            matches = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        if not isinstance(matches, list):
            continue
        for m in matches:
            comp = (m.get("competition") or {})
            seas = (m.get("season") or {})
            for side in ("home_team", "away_team"):
                team = m.get(side) or {}
                managers = team.get("managers") or [{}]
                for mgr in managers:
                    rows.append(
                        {
                            "match_id": m.get("match_id"),
                            "match_date": m.get("match_date"),
                            "competition_id": comp.get("competition_id"),
                            "competition": comp.get("competition_name"),
                            "country": comp.get("country_name"),
                            "season_id": seas.get("season_id"),
                            "season": seas.get("season_name"),
                            "side": side.replace("_team", ""),
                            "team_id": team.get(f"{side}_id"),
                            "team": team.get(f"{side}_name"),
                            "manager_id": mgr.get("id"),
                            "manager": mgr.get("nickname") or mgr.get("name"),
                        }
                    )
    df = pd.DataFrame(rows)
    df["match_date"] = pd.to_datetime(df["match_date"], errors="coerce")
    return df
