"""
Matplotlib fallback for the report figures (radar chart and PCA scatter for
Erling Haaland versus the three managers), used because the plotly/kaleido
static export path requires a local Chrome install that is not available in
this environment. Visually equivalent in content to the app's plotly charts.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

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
cluster_labels_df = pd.read_csv(PROJECT_ROOT / "outputs" / "tables" / "cluster_labels.csv", index_col=0)


# Season_End_Year 2022 (2021/22) is the specific Haaland-Dortmund season used
# in the report's worked example: it is the one row, verified directly against
# universe_compatibility.parquet, where Guardiola actually is the best-fit
# manager (0.047 similarity vs Klopp 0.041 and De Zerbi 0.032). Other Haaland
# seasons at Dortmund have Klopp as the best fit instead, so the specific row
# matters and must not be picked by "most minutes played" alone.
player_row = universe[
    (universe.Player == "Erling Haaland") & (universe.Squad == "Dortmund") & (universe.Season_End_Year == 2022)
].iloc[0]

# ---- Radar chart ----
labels = [DIMENSION_LABELS[d] for d in DIM_COLS]
angles = np.linspace(0, 2 * np.pi, len(DIM_COLS), endpoint=False).tolist()
angles += angles[:1]

fig, ax = plt.subplots(figsize=(9, 9), subplot_kw={"polar": True})
fig.patch.set_facecolor("white")

player_vals = list(player_row[DIM_COLS].fillna(0).astype(float).values)
player_vals += player_vals[:1]
ax.plot(angles, player_vals, color="#111111", linewidth=3, label="Erling Haaland (Dortmund)")
ax.fill(angles, player_vals, color="#111111", alpha=0.12)

for m in MANAGERS:
    vals = list(mp_indexed.loc[m, DIM_COLS].astype(float).values)
    vals += vals[:1]
    ax.plot(angles, vals, color=MANAGER_COLORS[m], linewidth=2.5, label=m)
    ax.fill(angles, vals, color=MANAGER_COLORS[m], alpha=0.12)

ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels, fontsize=12)
ax.set_title("Erling Haaland versus the three managers", fontsize=17, pad=40, weight="bold")
ax.tick_params(axis='y', labelsize=9)
ax.spines['polar'].set_color('#cccccc')
ax.grid(color='#dddddd')
ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.22), fontsize=11, frameon=False, ncol=2)
plt.tight_layout()
plt.savefig(OUT / "app_radar_haaland.png", dpi=170, bbox_inches="tight", facecolor="white")
plt.close()
print("saved radar")

# ---- PCA scatter ----
palette = ["#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A"]
fig2, ax2 = plt.subplots(figsize=(11, 8))
fig2.patch.set_facecolor("white")
for c in sorted(universe.cluster.dropna().unique()):
    sub = universe[universe.cluster == c]
    label = cluster_labels_df.loc[int(c), "label"] if int(c) in cluster_labels_df.index else str(c)
    ax2.scatter(sub.pca_x, sub.pca_y, s=10, alpha=0.35, color=palette[int(c) % len(palette)], label=f"{int(c)}: {label}")

ax2.scatter([player_row.pca_x], [player_row.pca_y], s=420, color="black", marker="*", zorder=5, label="Erling Haaland")
ax2.annotate("Erling Haaland", (player_row.pca_x, player_row.pca_y), textcoords="offset points",
             xytext=(12, 12), fontsize=13, weight="bold")
ax2.set_xlabel("Principal component 1", fontsize=12)
ax2.set_ylabel("Principal component 2", fontsize=12)
ax2.set_title("The full player universe, with Erling Haaland highlighted", fontsize=17, weight="bold")
ax2.legend(loc="upper left", fontsize=10, frameon=True, facecolor="white")
ax2.set_facecolor("white")
ax2.grid(color="#eeeeee")
for spine in ax2.spines.values():
    spine.set_color("#cccccc")
plt.tight_layout()
plt.savefig(OUT / "app_pca_haaland.png", dpi=170, bbox_inches="tight", facecolor="white")
plt.close()
print("saved pca")
