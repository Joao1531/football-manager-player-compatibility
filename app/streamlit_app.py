"""
Streamlit app: browse any player from the top-5 European leagues (2017/18-
2022/23), see their compatibility with Guardiola/Klopp/De Zerbi's playing
philosophies, and compare against other players/clusters.

Run with:  streamlit run app/streamlit_app.py
(run from the project root, or `cd` there first -- paths below are relative
to the project root via PROJECT_ROOT).

Data sources (all pre-computed by notebooks 02-06, nothing is recomputed
live): data/processed/player_universe.parquet, universe_compatibility.parquet,
manager_profiles.parquet. Player/manager photos are looked up live and
cached, see app/images.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from football_features import DIMENSION_WEIGHTS  # noqa: E402
from compatibility import DIMENSION_LABELS, explain_player_manager_fit  # noqa: E402
from images import MANAGER_WIKI_TITLES, render_photo  # noqa: E402

DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DIM_COLS = list(DIMENSION_WEIGHTS.keys())
MANAGERS = ["Pep Guardiola", "Jürgen Klopp", "Roberto De Zerbi"]
MANAGER_COLORS = {"Pep Guardiola": "#d62728", "Jürgen Klopp": "#1f77b4", "Roberto De Zerbi": "#2ca02c"}
PLAYER_COLOR = "#D4AF37"
CHART_LAYOUT = dict(
    template="plotly_white",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#1A1A1A"),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
)

st.set_page_config(page_title="Manager-Player Compatibility Explorer", layout="wide", page_icon="⚽")

# --------------------------------------------------------------------------
# Data loading (cached)
# --------------------------------------------------------------------------


@st.cache_data
def load_data():
    universe = pd.read_parquet(DATA_PROCESSED / "player_universe.parquet")
    compat = pd.read_parquet(DATA_PROCESSED / "universe_compatibility.parquet")
    manager_profiles = pd.read_parquet(DATA_PROCESSED / "manager_profiles.parquet")
    cluster_labels = pd.read_csv(PROJECT_ROOT / "outputs" / "tables" / "cluster_labels.csv", index_col=0)
    formation_profiles = pd.read_csv(PROJECT_ROOT / "outputs" / "tables" / "manager_formation_profile.csv")
    universe = universe.reset_index(drop=True)
    universe["season_label"] = (universe.Season_End_Year - 1).astype(str) + "/" + universe.Season_End_Year.astype(str).str[-2:]
    universe["player_label"] = universe.Player + " (" + universe.Pos + ", " + universe.Min.astype(int).astype(str) + " min)"
    return universe, compat, manager_profiles, cluster_labels, formation_profiles


universe, compat, manager_profiles, cluster_labels_df, formation_profiles_df = load_data()
mp_indexed = manager_profiles.set_index("manager")


def radar_trace(values, name, color):
    return go.Scatterpolar(
        r=list(values) + [values[0]],
        theta=[DIMENSION_LABELS[d] for d in DIM_COLS] + [DIMENSION_LABELS[DIM_COLS[0]]],
        name=name,
        line=dict(color=color),
        fill="toself",
        opacity=0.5,
    )


# --------------------------------------------------------------------------
# Sidebar: cascading player selection -- Season -> League -> Club -> Player
# --------------------------------------------------------------------------

st.sidebar.title("⚽ Find a player")

season_options = sorted(universe.season_label.unique(), reverse=True)
season_label = st.sidebar.selectbox("1. Season", season_options)
pool = universe[universe.season_label == season_label]

league_options = sorted(pool.Comp.unique())
league = st.sidebar.selectbox("2. League", league_options)
pool = pool[pool.Comp == league]

club_options = sorted(pool.Squad.unique())
club = st.sidebar.selectbox("3. Club", club_options)
pool = pool[pool.Squad == club]

roster_search = st.sidebar.text_input("Filter this club's roster (optional)")
if roster_search:
    pool = pool[pool.Player.str.contains(roster_search, case=False, na=False)]

pool = pool.sort_values("Min", ascending=False)
if pool.empty:
    st.sidebar.warning("No players match this filter.")
    st.stop()

player_label = st.sidebar.selectbox("4. Player", pool.player_label.tolist())
player_row = pool[pool.player_label == player_label].iloc[0]

st.sidebar.markdown("---")
with st.sidebar.expander("Or jump to any player by name"):
    quick_query = st.text_input("Search across all leagues/seasons")
    if quick_query:
        quick_pool = universe[universe.Player.str.contains(quick_query, case=False, na=False)]
        if not quick_pool.empty:
            quick_key = quick_pool.Player + " — " + quick_pool.Squad + " (" + quick_pool.season_label + ")"
            pick = st.selectbox("Matches", quick_key.tolist())
            if pick:
                player_row = quick_pool.iloc[list(quick_key).index(pick)]

st.sidebar.markdown("---")
st.sidebar.caption(
    "Data: top-5 European leagues (England, Spain, Italy, Germany, France), "
    "2017/18–2022/23 seasons. South American leagues were checked for "
    "availability and found not to have comparable passing/possession/"
    "defensive statistics in any accessible source — see "
    "`outputs/audit/data_availability_matrix.md`."
)

# --------------------------------------------------------------------------
# Header
# --------------------------------------------------------------------------

st.title("Manager–Player Compatibility Explorer")
st.caption("Knowledge-informed playing-style modelling — Guardiola · Klopp · De Zerbi")

hcol1, hcol2 = st.columns([1, 5])
with hcol1:
    render_photo(player_row.Player, width=110)
with hcol2:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Player", player_row.Player)
    c2.metric("Club", player_row.Squad)
    c3.metric("Position", player_row.Pos)
    c4.metric("Minutes played", f"{int(player_row.Min):,}")
    st.caption(f"{player_row.Comp} · {player_row.season_label}")

st.warning(
    "⚠️ **Read before trusting these numbers.** This project's own evaluation found the "
    "underlying model separates these three managers only moderately better than chance "
    "(42.1% best-fit accuracy vs. a ~34% empirical chance baseline, 95% confidence interval "
    "[37.8%, 46.2%], permutation-test p=0.0002 — statistically significant but not precisely "
    "known — after fixing real data-integrity issues and refining the features with "
    "football-analytical judgement: role-based positions, possession-adjusted pressing, "
    "goalkeeper distribution) — squad/league resourcing strength still contributes to the "
    "signal alongside managerial philosophy. Pressing intensity is the strongest, most "
    "theoretically-grounded discriminating dimension. Full honest writeup: "
    "`outputs/results/task4_evaluation_findings.md`. Treat every score below as illustrative "
    "of the *method*, not as a validated recruitment tool.",
    icon="⚠️",
)

player_compat = compat[
    (compat.Player == player_row.Player) & (compat.Season_End_Year == player_row.Season_End_Year) & (compat.team == player_row.Squad)
].sort_values("compatibility_similarity", ascending=False)

# --------------------------------------------------------------------------
# Tabs
# --------------------------------------------------------------------------

tab_fit, tab_profile, tab_cluster, tab_compare = st.tabs(
    ["🎯 Manager Fit", "📊 Tactical Profile", "🧩 Playing-Style Cluster", "🔁 Compare Players"]
)

with tab_fit:
    st.header("Manager fit")
    if player_compat.empty:
        st.info("No compatibility scores available for this player-season.")
    else:
        best_row = player_compat.iloc[0]
        cols = st.columns(3)
        for i, (_, row) in enumerate(player_compat.iterrows()):
            with cols[i]:
                pcol1, pcol2 = st.columns([1, 2])
                with pcol1:
                    render_photo(MANAGER_WIKI_TITLES[row.scored_against_manager], width=64)
                with pcol2:
                    flag = " ⚠️" if row.low_confidence else ""
                    st.metric(
                        row.scored_against_manager,
                        f"{row.compatibility_index_0_100:.0f} / 100{flag}",
                        f"similarity {row.compatibility_similarity:+.3f} · {row.n_dims_used}/7 dims",
                    )
        st.caption("Index is a rescaled cosine similarity, NOT a probability — see project brief §23 and `src/compatibility.py`.")

        st.subheader(f"Best fit: {best_row.scored_against_manager}")
        explanation = explain_player_manager_fit(
            best_row, player_row[DIM_COLS], mp_indexed.loc[best_row.scored_against_manager], DIM_COLS
        )
        ecol1, ecol2 = st.columns(2)
        with ecol1:
            st.markdown("**Why this fit — data-derived evidence:**")
            for s in explanation["data_derived_evidence"]:
                st.markdown(f"- ✅ {s}")
        with ecol2:
            st.markdown("**Limiting factors:**")
            for s in explanation["limiting_factors"]:
                st.markdown(f"- ⚠️ {s}")

with tab_profile:
    st.header("Tactical profile comparison")
    compare_managers = st.multiselect("Compare against", MANAGERS, default=MANAGERS, key="profile_managers")
    fig = go.Figure()
    player_vals = player_row[DIM_COLS].fillna(0).astype(float).values
    fig.add_trace(radar_trace(player_vals, f"{player_row.Player}", PLAYER_COLOR))
    for m in compare_managers:
        fig.add_trace(radar_trace(mp_indexed.loc[m, DIM_COLS].astype(float).values, m, MANAGER_COLORS[m]))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True)), height=550, showlegend=True, **CHART_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Raw dimension scores** (z-scored vs. the big-5-league position baseline)")
    table = pd.DataFrame({"Dimension": [DIMENSION_LABELS[d] for d in DIM_COLS], player_row.Player: player_row[DIM_COLS].values})
    for m in compare_managers:
        table[m] = mp_indexed.loc[m, DIM_COLS].values
    st.dataframe(table.round(3), use_container_width=True, hide_index=True)

    with st.expander("Manager formation profiles (descriptive, not part of the score above)"):
        st.markdown(
            "Each manager's starting-formation tendency across their full covered tenure, "
            "derived from match-level `Home_Formation`/`Away_Formation` data. This is reported "
            "as **descriptive supporting evidence, not a tactical dimension**: formation is "
            "only available for the 22 club-seasons in the manager-attributed sample, too small "
            "a population to z-score safely the way the 7 dimensions above are — see "
            "`decision_log.md` D-008."
        )
        st.dataframe(
            formation_profiles_df.rename(columns={
                "manager": "Manager", "n_matches": "Matches", "modal_formation": "Modal formation",
                "formation_stability": "Formation stability", "n_distinct_formations": "Distinct formations used",
                "mean_back_line_size": "Mean back-line size",
            }).round(3),
            use_container_width=True, hide_index=True,
        )
        st.caption(
            "Klopp is by far the most tactically settled (86.5% of matches in his modal 4-3-3). "
            "De Zerbi is the most structurally fluid by every measure here — the most distinct "
            "formations used and the lowest mean back-line size — corroborating his qualitative "
            "description elsewhere in this project as an unconventional, fluid tactician."
        )

with tab_cluster:
    st.header("Playing-style cluster")
    cluster_id = player_row.get("cluster")
    cluster_label = player_row.get("cluster_label")
    if pd.notna(cluster_id):
        st.markdown(
            f"This player-season falls into **cluster {int(cluster_id)}: {cluster_label}** "
            f"(one of 5 data-driven playing-style groups found via k-means clustering over the "
            f"same 7 dimensions — see `notebooks/06_clustering_and_visualization.ipynb`)."
        )
    fig2 = go.Figure()
    palette = ["#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A"]
    for c in sorted(universe.cluster.dropna().unique()):
        sub = universe[universe.cluster == c]
        fig2.add_trace(go.Scattergl(
            x=sub.pca_x, y=sub.pca_y, mode="markers",
            name=cluster_labels_df.loc[int(c), "label"] if int(c) in cluster_labels_df.index else str(c),
            marker=dict(size=4, opacity=0.35, color=palette[int(c) % len(palette)]),
        ))
    fig2.add_trace(go.Scattergl(
        x=[player_row.pca_x], y=[player_row.pca_y], mode="markers+text", name=player_row.Player,
        marker=dict(size=16, color=PLAYER_COLOR, symbol="star", line=dict(width=1, color="#1A1A1A")),
        text=[player_row.Player], textposition="top center", textfont=dict(color="#1A1A1A"),
    ))
    fig2.update_layout(
        height=600, xaxis_title="PC1", yaxis_title="PC2",
        title="Player universe (PCA projection) — this player highlighted", **CHART_LAYOUT,
    )
    st.plotly_chart(fig2, use_container_width=True)

with tab_compare:
    st.header("Similar players")

    def nearest_players(row, universe_df, n=10):
        vals = row[DIM_COLS].astype(float).values
        other = universe_df[(universe_df.Player != row.Player) | (universe_df.Season_End_Year != row.Season_End_Year)].copy()
        mat = other[DIM_COLS].astype(float).values
        mask = ~np.isnan(vals)
        if mask.sum() < 3:
            return other.iloc[0:0]
        diffs = mat[:, mask] - vals[mask]
        valid_rows = ~np.isnan(diffs).any(axis=1)
        other = other[valid_rows]
        diffs = diffs[valid_rows]
        dist = np.sqrt((diffs ** 2).sum(axis=1))
        other = other.assign(_dist=dist)
        return other.sort_values("_dist").head(n)

    similar = nearest_players(player_row, universe)
    if not similar.empty:
        st.dataframe(
            similar[["Player", "Squad", "Comp", "season_label", "Pos", "best_fit_manager", "cluster_label", "_dist"]]
            .rename(columns={"_dist": "distance", "Comp": "League", "season_label": "Season"})
            .round(3),
            use_container_width=True, hide_index=True,
        )

    st.header("Head-to-head")
    universe_keys = universe.Player + " — " + universe.Squad + " (" + universe.season_label + ")"
    compare_key = st.selectbox("Second player", ["(none)"] + universe_keys.tolist(), key="compare_select")
    if compare_key != "(none)":
        other_row = universe[universe_keys == compare_key].iloc[0]
        pcol1, pcol2, pcol3 = st.columns([1, 3, 1])
        with pcol1:
            render_photo(player_row.Player, width=90)
        with pcol3:
            render_photo(other_row.Player, width=90)

        fig3 = go.Figure()
        player_vals2 = player_row[DIM_COLS].fillna(0).astype(float).values
        fig3.add_trace(radar_trace(player_vals2, player_row.Player, PLAYER_COLOR))
        fig3.add_trace(radar_trace(other_row[DIM_COLS].fillna(0).astype(float).values, other_row.Player, "#4FC3F7"))
        fig3.update_layout(polar=dict(radialaxis=dict(visible=True)), height=500, **CHART_LAYOUT)
        st.plotly_chart(fig3, use_container_width=True)

        comp_table = pd.DataFrame({
            "Dimension": [DIMENSION_LABELS[d] for d in DIM_COLS],
            player_row.Player: player_row[DIM_COLS].values,
            other_row.Player: other_row[DIM_COLS].values,
        }).round(3)
        st.dataframe(comp_table, use_container_width=True, hide_index=True)

# --------------------------------------------------------------------------
# Footer
# --------------------------------------------------------------------------

with st.expander("About this project, methodology, and limitations"):
    st.markdown(
        """
This app is built on a knowledge-informed pipeline: raw FBref match/season statistics →
football concepts (progressive passing, pressing intensity, box presence, etc.) → 7
tactical dimensions, anchored on a published, discriminant-validated taxonomy
(Plakias et al., 2025, *JPES*) → manager and player profiles → compatibility scores.

**Known limitations (reported honestly, not hidden):**
- The compatibility score is a **cosine similarity**, not a calibrated probability.
- Best-fit accuracy against real managerial assignment is **42.1%** (95% bootstrap
  confidence interval [37.8%, 46.2%], n=561), against an empirical chance baseline of
  **~34%** for 3 classes (this sample's real manager mix, not a perfectly even 1-in-3). A
  permutation test confirms this is statistically significant (p=0.0002) — but the interval
  is wide enough that the 42.1% figure should be read as "high 30s to mid 40s," not as a
  precise number. Squad/league resourcing strength still contributes to the signal alongside
  managerial philosophy in this feature set.
- **Pressing intensity** is the strongest dimension by far (permutation importance +7.5
  percentage points). It cleanly confirms De Zerbi's predicted low-press, in-possession
  identity (his score sits well below both other managers), but Guardiola's clubs actually
  score marginally *higher* than Klopp's on this dimension — the opposite of the popular
  gegenpressing narrative, most likely because Manchester City's extreme possession dominance
  over-corrects the possession adjustment upward. Individual defending, buildup directness,
  progressive passing and progressive carrying also carry real signal once positions were
  role-refined; box presence and chance creation do not (both are mildly negative — the role
  refinement rescued individual defending but not box presence).
- Refining player positions into 8 tactical roles (instead of 4 coarse buckets),
  possession-adjusting pressing stats, and adding goalkeeper distribution features
  (build-up style) improved best-fit accuracy from 33% to 42% — role precision and
  football-analytical judgement mattered as much as raw data volume.
- **Starting formation** (see the "Manager formation profiles" expander in the Tactical
  Profile tab) was explored as an eighth tactical dimension but is reported descriptively
  instead, because it is only available for the 22 club-seasons in the manager-attributed
  sample — too small a population to standardise safely alongside the other 7 dimensions.
- South American leagues are **not included** — checked directly across every accessible
  data source (FBref mirror, Understat, StatsBomb); none provide comparable
  passing/possession/defensive statistics for Brazilian or Argentine leagues.
- Guardiola and Klopp's profiles are single-club (Manchester City, Liverpool) within the
  covered data window; only De Zerbi's spans multiple clubs (Sassuolo, Brighton, Marseille).
- Player/manager photos are looked up live from Wikipedia by name matching — best-effort,
  not guaranteed correct for players with common names or no Wikipedia page.

Full documentation: `outputs/PHASE0_DELIVERABLE.md`, `outputs/results/task4_evaluation_findings.md`,
`report/memoria.md`.
"""
    )
