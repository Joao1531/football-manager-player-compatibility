"""
Regenerates the exact charts shown in the Streamlit app as static, high
resolution PNG files for embedding in the written report. Uses the same
plotting logic as app/streamlit_app.py so the report figures are visually
identical to what a user of the live app actually sees.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "app"))

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

from football_features import DIMENSION_WEIGHTS
from compatibility import DIMENSION_LABELS

DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
OUT = Path(__file__).resolve().parent
DIM_COLS = list(DIMENSION_WEIGHTS.keys())
MANAGER_COLORS = {"Pep Guardiola": "#d62728", "Jürgen Klopp": "#1f77b4", "Roberto De Zerbi": "#2ca02c"}
MANAGERS = ["Pep Guardiola", "Jürgen Klopp", "Roberto De Zerbi"]

universe = pd.read_parquet(DATA_PROCESSED / "player_universe.parquet")
manager_profiles = pd.read_parquet(DATA_PROCESSED / "manager_profiles.parquet")
mp_indexed = manager_profiles.set_index("manager")

player_row = universe[(universe.Player == "Erling Haaland") & (universe.Squad == "Dortmund")].sort_values("Min", ascending=False).iloc[0]


def radar_trace(values, name, color):
    return go.Scatterpolar(
        r=list(values) + [values[0]],
        theta=[DIMENSION_LABELS[d] for d in DIM_COLS] + [DIMENSION_LABELS[DIM_COLS[0]]],
        name=name, line=dict(color=color, width=3), fill="toself", opacity=0.45,
    )


fig = go.Figure()
player_vals = player_row[DIM_COLS].fillna(0).astype(float).values
fig.add_trace(radar_trace(player_vals, "Erling Haaland (Dortmund)", "#111111"))
for m in MANAGERS:
    fig.add_trace(radar_trace(mp_indexed.loc[m, DIM_COLS].astype(float).values, m, MANAGER_COLORS[m]))
fig.update_layout(
    polar=dict(radialaxis=dict(visible=True, gridcolor="#dddddd"), bgcolor="white"),
    height=700, width=900, showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
    title=dict(text="Erling Haaland versus the three managers", x=0.5, font=dict(size=20)),
    paper_bgcolor="white", font=dict(size=13),
)
pio.write_image(fig, str(OUT / "app_radar_haaland.png"), scale=2)
print("saved radar")

palette = ["#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A"]
cluster_labels_df = pd.read_csv(PROJECT_ROOT / "outputs" / "tables" / "cluster_labels.csv", index_col=0)

fig2 = go.Figure()
for c in sorted(universe.cluster.dropna().unique()):
    sub = universe[universe.cluster == c]
    label = cluster_labels_df.loc[int(c), "label"] if int(c) in cluster_labels_df.index else str(c)
    fig2.add_trace(go.Scattergl(x=sub.pca_x, y=sub.pca_y, mode="markers", name=f"{int(c)}: {label}",
                                 marker=dict(size=5, opacity=0.35, color=palette[int(c) % len(palette)])))
fig2.add_trace(go.Scattergl(x=[player_row.pca_x], y=[player_row.pca_y], mode="markers+text",
                             name="Erling Haaland", marker=dict(size=22, color="black", symbol="star"),
                             text=["Erling Haaland"], textposition="top center", textfont=dict(size=14)))
fig2.update_layout(height=750, width=1000, xaxis_title="Principal component 1", yaxis_title="Principal component 2",
                    title=dict(text="The full player universe, with Erling Haaland highlighted", x=0.5, font=dict(size=20)),
                    paper_bgcolor="white", plot_bgcolor="white", font=dict(size=13),
                    legend=dict(font=dict(size=11)))
fig2.update_xaxes(gridcolor="#eeeeee")
fig2.update_yaxes(gridcolor="#eeeeee")
pio.write_image(fig2, str(OUT / "app_pca_haaland.png"), scale=2)
print("saved pca")
