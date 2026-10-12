"""
Player -> manager compatibility scoring and football-language explanation.

Scientific definition of the score (brief SS23): cosine similarity between a
player's tactical-dimension vector and a manager's centroid vector, over the
7 dimensions built in football_features.py. This is a SIMILARITY score, not
a probability and not a calibrated classifier output -- it is reported as
such throughout, per the brief's explicit instruction never to call an
uncalibrated score a probability.

Explanation method (brief SS26, SS33-34): each dimension's contribution to
the similarity is decomposed as player_z_i * manager_centroid_z_i (the
per-term product that cosine similarity sums over, before normalisation).
Ranking dimensions by this signed contribution gives a football-language,
evidence-traceable account of *why* a player matches a manager -- every
explanatory sentence is generated from an actual number in this table, per
the brief's non-negotiable requirement (SS7-8).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

DIMENSION_LABELS = {
    "TD1_buildup_directness": "build-up / possession-based play",
    "TD3_progression_passing": "progressive passing",
    "TD4_progression_carrying": "progressive carrying",
    "TD6_chance_creation": "chance creation",
    "TD7_box_presence": "box presence / attacking threat",
    "TD9_pressing_intensity": "pressing intensity",
    "TD11_individual_defending": "individual defending / duels",
}


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def masked_cosine_similarity(a: np.ndarray, b: np.ndarray) -> tuple[float, int]:
    """Cosine similarity computed only over dimensions where BOTH vectors
    have a value -- returns (similarity, n_dims_used). Use this instead of
    cosine_similarity whenever either vector may contain NaN (e.g. any
    profile touching Sassuolo/Benevento, see decision_log.md D-006)."""
    available = ~np.isnan(a) & ~np.isnan(b)
    n = int(available.sum())
    if n == 0:
        return np.nan, 0
    return cosine_similarity(a[available], b[available]), n


def masked_cosine_similarity_matrix(vecs: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Pairwise masked cosine similarity for a set of vectors (rows).
    Returns (similarity_matrix, n_dims_used_matrix)."""
    k = len(vecs)
    sim = np.full((k, k), np.nan)
    ndims = np.zeros((k, k), dtype=int)
    for i in range(k):
        for j in range(k):
            sim[i, j], ndims[i, j] = masked_cosine_similarity(vecs[i], vecs[j])
    return sim, ndims


def compute_compatibility(
    player_profiles: pd.DataFrame,
    manager_profiles: pd.DataFrame,
    dim_cols: list[str],
    min_dims_required: int = 4,
) -> pd.DataFrame:
    """One row per (player-season, manager they are being scored against),
    for every player x every manager (not only the manager they actually
    played under) -- this is what makes the compatibility comparison
    meaningful (brief SS23-24, SS34).

    Some player-seasons are missing several dimensions entirely (Sassuolo
    and Benevento players, 2018-2021 -- the FBref match-level 'passing',
    'passing_types', 'possession' and 'keeper' blocks are not populated for
    Serie A before 2023/24, see decision_log.md D-006). Rather than treat a
    missing dimension as zero (misrepresenting "no data" as "exactly average"
    -- the bug documented in outputs/results/task4_evaluation_findings.md),
    similarity is computed only over the dimensions BOTH the player and the
    manager centroid have a value for, and the number of dimensions actually
    used is recorded (`n_dims_used`) so a thin comparison is visible, not
    hidden. Comparisons using fewer than `min_dims_required` dimensions are
    flagged `low_confidence=True` rather than dropped, so the caller can
    decide whether to exclude them.
    """
    centroids = manager_profiles.set_index("manager")[dim_cols]
    rows = []
    for _, prow in player_profiles.iterrows():
        pvec_full = prow[dim_cols].to_numpy(dtype=float)
        for manager, mvec_full in centroids.iterrows():
            mvec_full = mvec_full.to_numpy(dtype=float)
            available = ~np.isnan(pvec_full) & ~np.isnan(mvec_full)
            n_dims = int(available.sum())
            pvec, mvec = pvec_full[available], mvec_full[available]
            sim = cosine_similarity(pvec, mvec) if n_dims > 0 else np.nan
            contributions = np.full(len(dim_cols), np.nan)
            contributions[available] = pvec * mvec
            rows.append({
                "Player": prow["Player"],
                "Player_Href": prow["Player_Href"],
                "actual_manager": prow["manager"],
                "team": prow["team"],
                "Season_End_Year": prow["Season_End_Year"],
                "Pos": prow["Pos"],
                "scored_against_manager": manager,
                "compatibility_similarity": sim,
                "n_dims_used": n_dims,
                "low_confidence": n_dims < min_dims_required,
                **{f"contrib__{d}": contributions[i] for i, d in enumerate(dim_cols)},
            })
    return pd.DataFrame(rows)


def rescale_to_index(sim_series: pd.Series) -> pd.Series:
    """A 0-100 'compatibility index' for human-readable reporting --
    an explicitly-labelled min-max rescaling of the cosine similarity across
    this player x manager comparison set, NOT a probability (brief SS23)."""
    lo, hi = sim_series.min(), sim_series.max()
    if hi == lo:
        return pd.Series(50.0, index=sim_series.index)
    return 100 * (sim_series - lo) / (hi - lo)


def explain_player_manager_fit(
    compat_row: pd.Series,
    player_dims: pd.Series,
    manager_dims: pd.Series,
    dim_cols: list[str],
    top_n: int = 3,
) -> dict:
    """Builds the three-evidence-type explanation structure (brief SS26):
    data-derived evidence, football interpretation, managerial relevance --
    from the actual contribution numbers, never invented."""
    contribs = pd.Series(
        {d: compat_row[f"contrib__{d}"] for d in dim_cols}
    ).dropna().sort_values(ascending=False)

    strengths = contribs.head(top_n)
    weaknesses = contribs.tail(top_n)[contribs.tail(top_n) < 0]

    def sentence(dim, value, player_z):
        label = DIMENSION_LABELS[dim]
        direction = "well above" if player_z > 0.5 else "above" if player_z > 0 else "below"
        return (
            f"{label}: player z-score {player_z:+.2f} ({direction} the league average for the position), "
            f"contributing {value:+.3f} to the similarity with {compat_row['scored_against_manager']}."
        )

    return {
        "player": compat_row["Player"],
        "season": compat_row["Season_End_Year"],
        "manager": compat_row["scored_against_manager"],
        "compatibility_similarity": compat_row["compatibility_similarity"],
        "data_derived_evidence": [
            sentence(d, contribs[d], player_dims[d]) for d in strengths.index
        ],
        "limiting_factors": [
            sentence(d, contribs[d], player_dims[d]) for d in weaknesses.index
        ] if len(weaknesses) else ["No dimension pulls materially against this fit."],
    }
