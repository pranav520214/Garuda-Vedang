#!/usr/bin/env python3
"""Create presentation-ready Garuda Vedang impact and reach charts."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec


try:
    plt.style.use("seaborn-v0_8-whitegrid")
except OSError:
    plt.style.use("seaborn-whitegrid")

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.titlesize": 14,
        "axes.labelsize": 11,
        "figure.facecolor": "white",
        "axes.facecolor": "#F8FAFC",
        "axes.edgecolor": "#CBD5E1",
        "grid.color": "#CBD5E1",
        "grid.alpha": 0.45,
    }
)

# Approximate / illustrative values retained from the original presentation.
years = ["2000\n(peak)", "2002", "2007", "2018", "2023"]
india_affected = [50.1, 42.0, 38.1, 23.1, 10.8]

impact_labels = ["People affected\n(floods)", "Flood deaths", "Disaster\n displacements"]
# Display values are normalized only so fundamentally different units can be
# compared visually. The labels above the bars show the actual values.
global_impact = [32.0, 21.8, 26.5]
india_impact = [6.29, 3.6, 3.2]
global_actual = ["3.2B", "218k", "265M"]
india_actual = ["629M", "36k", "32M"]

regions = [
    "India\n(high-risk states)",
    "South Asia\n(excl. India)",
    "Southeast\nAsia",
    "Other\nflood-prone",
]
exposed_population = [25, 18, 22, 30]
drone_reach = [8, 4, 5, 3]


def add_value_labels(axis, bars, labels, color="#334155"):
    """Place readable values above a bar group."""
    for bar, label in zip(bars, labels):
        axis.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.7,
            label,
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
            color=color,
        )


fig = plt.figure(figsize=(16, 11))
gs = GridSpec(
    2,
    2,
    figure=fig,
    height_ratios=[1, 1.15],
    top=0.88,
    bottom=0.11,
    hspace=0.42,
    wspace=0.24,
)

# Graph 1: India flood impact.
ax1 = fig.add_subplot(gs[0, 0])
x = np.arange(len(years))
bars = ax1.bar(
    x, india_affected, color="#C2413B", edgecolor="white", width=0.62, zorder=3
)
ax1.plot(x, india_affected, color="#7F1D1D", marker="o", linewidth=2, zorder=4)
add_value_labels(
    ax1, bars, [f"{value:.1f}M" for value in india_affected], color="#7F1D1D"
)
ax1.set_title("India: People Affected by Major Flood Events", fontweight="bold")
ax1.set_ylabel("People affected (millions)")
ax1.set_xticks(x, years)
ax1.set_ylim(0, 60)
ax1.annotate(
    "~365M people affected by floods\nin India (2000–2025)",
    xy=(3, 23.1),
    xytext=(2.0, 48),
    arrowprops={"arrowstyle": "->", "color": "#64748B"},
    fontsize=9,
    color="#475569",
)

# Graph 2: global versus India.
ax2 = fig.add_subplot(gs[0, 1])
x2 = np.arange(len(impact_labels))
width = 0.36
global_bars = ax2.bar(
    x2 - width / 2,
    global_impact,
    width,
    label="Global",
    color="#2563EB",
    edgecolor="white",
    zorder=3,
)
india_bars = ax2.bar(
    x2 + width / 2,
    india_impact,
    width,
    label="India",
    color="#C2413B",
    edgecolor="white",
    zorder=3,
)
add_value_labels(ax2, global_bars, global_actual, color="#1D4ED8")
add_value_labels(ax2, india_bars, india_actual, color="#7F1D1D")
ax2.set_title("Global vs India: Disaster Impact Comparison", fontweight="bold")
ax2.set_ylabel("Normalized display scale")
ax2.set_xticks(x2, impact_labels)
ax2.set_ylim(0, 40)
ax2.legend(frameon=False, loc="upper right")
ax2.text(
    0.5,
    -0.18,
    "Labels show actual values. Bar heights are normalized because\n"
    "people affected, deaths and displacements use different units.",
    transform=ax2.transAxes,
    ha="center",
    fontsize=8,
    color="#64748B",
)

# Graph 3: potential reach, full width.
ax3 = fig.add_subplot(gs[1, :])
x4 = np.arange(len(regions))
exposed_bars = ax3.bar(
    x4 - width / 2,
    exposed_population,
    width,
    label="High-risk / exposed population",
    color="#F59E0B",
    edgecolor="white",
    zorder=3,
)
reach_bars = ax3.bar(
    x4 + width / 2,
    drone_reach,
    width,
    label="Potential drone reach",
    color="#16A34A",
    edgecolor="white",
    zorder=3,
)
add_value_labels(
    ax3, exposed_bars, [f"{value:.0f}M" for value in exposed_population],
    color="#92400E",
)
add_value_labels(
    ax3, reach_bars, [f"{value:.0f}M" for value in drone_reach],
    color="#166534",
)
ax3.set_title("Potential Reach of Garuda Vedang", fontweight="bold")
ax3.set_ylabel("People (millions)")
ax3.set_xticks(x4, regions)
ax3.set_ylim(0, 36)
ax3.legend(frameon=False, fontsize=9, loc="upper right")
ax3.text(
    0.02,
    0.94,
    "Even moderate national deployment can support search & rescue for "
    "several million people every year in hard-to-reach areas.",
    transform=ax3.transAxes,
    va="top",
    fontsize=10,
    fontweight="bold",
    color="#166534",
    bbox={
        "boxstyle": "round,pad=0.6",
        "facecolor": "#F0FDF4",
        "edgecolor": "#16A34A",
        "alpha": 0.97,
    },
)

fig.suptitle(
    "Garuda Vedang – Potential Impact: Lives & People We Can Reach",
    fontsize=19,
    fontweight="bold",
    color="#0F172A",
)
fig.text(
    0.5,
    0.005,
    "Sources: EM-DAT, IDMC, UNDRR and national reports (approximate figures). "
    "Potential reach is illustrative and depends on deployment and response integration.",
    ha="center",
    fontsize=8,
    style="italic",
    color="#64748B",
)

repo_root = Path(__file__).resolve().parent.parent
output_path = repo_root / "assets" / "cfd_renders" / "Garuda_Vedang_Impact.png"
fig.savefig(output_path, dpi=150, facecolor="white")
plt.close(fig)
print(f"Graph saved as: {output_path}")
