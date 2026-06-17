#!/usr/bin/env python3
"""Regenerate TxBench-PP result figures from internal result tables."""
from __future__ import annotations

import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-cache")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.font_manager import FontProperties

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "paper" / "figures"
RESULTS = ROOT.parent / "txbench_internal" / "results"
EVALS = ROOT.parent / "txbench_internal" / "evals"

TEXT = "#15191F"
MUTED = "#5F6872"
GRID = "#D9DEE5"
AXIS = "#AFA89B"
CREAM = "#EEE8DC"
CREAM_LIGHT = "#F8F5EE"
ACCENT = "#A95F3D"
ACCENT_LIGHT = "#C97745"
TEAL = "#2A9D8F"
TEAL_LIGHT = "#A9CEC4"
VIOLET = "#7267C8"
GOLD = "#B89142"
GRAY = "#B8B2AA"
GRAY_DARK = "#8D867E"

SERIF_STACK = ["DejaVu Serif", "serif"]
SERIF = FontProperties(family=SERIF_STACK)
SERIF_BOLD = FontProperties(family=SERIF_STACK, weight="bold")

plt.rcParams.update(
    {
        "font.family": SERIF_STACK,
        "font.serif": SERIF_STACK,
        "font.size": 8.0,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "axes.edgecolor": AXIS,
        "axes.labelcolor": TEXT,
        "axes.titlecolor": TEXT,
        "xtick.color": MUTED,
        "ytick.color": TEXT,
        "text.color": TEXT,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)

HARNESS_COLORS = {
    "pi": ACCENT,
    "claude-code": TEAL,
    "openai-codex": VIOLET,
}


def save(fig: plt.Figure, stem: str) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(FIGURES / f"{stem}.{ext}", dpi=520, bbox_inches="tight")
    plt.close(fig)
    print(f"saved {stem}")


def model_label(model: str) -> str:
    labels = {
        "claude-opus-4-8": "Opus 4.8",
        "claude-opus-4-7": "Opus 4.7",
        "claude-opus-4-6": "Opus 4.6",
        "claude-sonnet-4-6": "Sonnet 4.6",
        "gpt-5.5": "GPT-5.5",
        "gpt-5.4": "GPT-5.4",
        "gemini-3.5-flash": "Gemini 3.5 Flash",
        "gemini-3.1-pro-preview": "Gemini 3.1 Pro",
        "kimi-k2p6": "Kimi K2P6",
        "grok-4.20-0309-reasoning": "Grok 4.20",
        "grok-4.3": "Grok 4.3",
    }
    return labels.get(model, model)


def harness_label(harness: str) -> str:
    return {
        "pi": "Pi",
        "claude-code": "Claude Code",
        "openai-codex": "Codex",
    }.get(harness, harness)


def harness_short_label(harness: str) -> str:
    return {
        "pi": "Pi",
        "claude-code": "Claude Code",
        "openai-codex": "Codex",
    }.get(harness, harness)


def task_label(task: str) -> str:
    labels = {
        "biomarker_discovery": "Biomarker discovery",
        "cell_typing": "Cell typing",
        "cheminformatics": "Cheminformatics",
        "differential_response": "Differential response",
        "dimensionality_reduction": "Dim. reduction",
        "dose_response": "Dose response",
        "drug_interaction": "Drug interaction",
        "exposure_pk": "Exposure / PK",
        "hit_prioritization": "Hit prioritization",
        "image_analysis": "Image analysis",
        "mechanism_of_action": "MoA",
        "normalization": "Normalization",
        "phenotype_classification": "Phenotype classification",
        "program_decision": "Program decision",
        "qc": "QC",
        "safety_assessment": "Safety",
        "selectivity_profiling": "Selectivity profiling",
        "target_assessment": "Target assessment",
        "target_dependency": "Target dependency",
        "target_engagement": "Target engagement",
    }
    return labels.get(task, task.replace("_", " ").title())


def load_metadata() -> pd.DataFrame:
    rows = []
    for path in EVALS.glob("*/eval.json"):
        data = json.loads(path.read_text())
        meta = data["metadata"]
        rows.append(
            {
                "task_id": data["id"],
                "task_file_name": f"{data['id']}.json",
                "tx_stage": meta.get("tx_stage"),
                "kit": meta.get("kit"),
                "task": meta.get("task"),
            }
        )
    return pd.DataFrame(rows)


def style_axis(ax: plt.Axes, *, xgrid: bool = True) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(AXIS)
    ax.spines["bottom"].set_color(AXIS)
    ax.tick_params(axis="both", labelsize=7.2)
    if xgrid:
        ax.grid(axis="x", color=GRID, linewidth=0.55, alpha=0.95)
        ax.set_axisbelow(True)


def plot_model_performance() -> None:
    model_results = pd.read_csv(RESULTS / "model_results.csv")
    raw = pd.read_csv(RESULTS / "results_table.csv")
    raw["passed"] = raw["passed"].astype(bool)

    pi_order = (
        model_results[model_results["harness"].eq("pi")]
        .sort_values("Accuracy (%)", ascending=False)["model_name"]
        .tolist()
    )
    y = np.arange(len(pi_order))

    fig, (ax_a, ax_b) = plt.subplots(
        1,
        2,
        figsize=(9.8, 4.25),
        gridspec_kw={"width_ratios": [1.28, 1.0], "wspace": 0.28},
    )

    offsets = {"pi": 0.0, "claude-code": -0.18, "openai-codex": 0.18}
    markers = {"pi": "o", "claude-code": "s", "openai-codex": "D"}
    for harness in ["pi", "claude-code", "openai-codex"]:
        rows = model_results[model_results["harness"].eq(harness)]
        for _, row in rows.iterrows():
            if row["model_name"] not in pi_order:
                continue
            yi = pi_order.index(row["model_name"]) + offsets[harness]
            acc = row["Accuracy (%)"]
            lo = acc - row["ci_lower"]
            hi = row["ci_upper"] - acc
            color = HARNESS_COLORS[harness]
            ax_a.errorbar(
                acc,
                yi,
                xerr=np.array([[lo], [hi]]),
                fmt=markers[harness],
                color=color,
                ecolor=color,
                markersize=4.5 if harness == "pi" else 4.0,
                elinewidth=0.85,
                capsize=2.2,
                capthick=0.75,
                zorder=3,
            )
            label_x = max(acc + 3.0, row["ci_upper"] + 1.2)
            ax_a.text(
                label_x,
                yi,
                f"{harness_short_label(harness)} {acc:.1f}%",
                fontsize=5.7,
                va="center",
                ha="left",
                color=color,
                bbox=dict(boxstyle="round,pad=0.16", fc=CREAM_LIGHT, ec="#D8CDBB", lw=0.42),
            )

    ax_a.set_yticks(y)
    ax_a.set_yticklabels([model_label(m) for m in pi_order])
    ax_a.invert_yaxis()
    ax_a.set_xlim(0, 100)
    ax_a.set_xlabel("Endpoint pass rate (%)", fontsize=8)
    ax_a.set_title("A  Pass rate by model and harness", loc="left", fontsize=9, fontproperties=SERIF_BOLD)
    style_axis(ax_a)
    handles = [
        plt.Line2D([0], [0], marker=markers[h], color="none", markerfacecolor=HARNESS_COLORS[h], markeredgecolor=HARNESS_COLORS[h], markersize=5, label=harness_label(h))
        for h in ["pi", "claude-code", "openai-codex"]
    ]
    ax_a.legend(handles=handles, frameon=False, fontsize=6.7, loc="lower right", title="Harness", title_fontsize=6.7)

    reliability = []
    pi = raw[raw["harness"].eq("pi")]
    for model in pi_order:
        by_task = pi[pi["model_name"].eq(model)].groupby("task_id")["passed"].sum()
        counts = by_task.value_counts().reindex([0, 1, 2, 3], fill_value=0).astype(int)
        reliability.append(counts)
    rel = pd.DataFrame(reliability, index=pi_order)
    colors = [CREAM, GRAY, TEAL, ACCENT_LIGHT]
    labels = ["0 passed", "1 passed", "2 passed", "3 passed"]
    left = np.zeros(len(pi_order))
    for i, col in enumerate([0, 1, 2, 3]):
        vals = rel[col].to_numpy()
        ax_b.barh(y, vals, left=left, height=0.66, color=colors[i], edgecolor="white", linewidth=0.45, label=labels[i])
        for yi, v, lft in zip(y, vals, left):
            if v >= 8:
                ax_b.text(lft + v / 2, yi, str(int(v)), ha="center", va="center", fontsize=5.9, color=TEXT if i < 3 else "white")
        left += vals
    ax_b.set_yticks(y)
    ax_b.set_yticklabels([])
    ax_b.invert_yaxis()
    ax_b.set_xlim(0, 100)
    ax_b.set_xlabel("Evaluations (n = 100)", fontsize=8)
    ax_b.set_title("B  Evaluations by passing attempts", loc="left", fontsize=9, fontproperties=SERIF_BOLD)
    style_axis(ax_b)
    ax_b.legend(frameon=False, fontsize=6.2, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.15), handlelength=1.2, columnspacing=1.0)

    save(fig, "model_performance")


def task_summary() -> tuple[pd.DataFrame, pd.DataFrame, list[str], list[str]]:
    meta = load_metadata()
    raw = pd.read_csv(RESULTS / "results_table.csv")
    raw["passed"] = raw["passed"].astype(bool)
    df = raw.merge(meta[["task_id", "task"]], on="task_id", how="left")
    pi = df[df["harness"].eq("pi")].copy()

    counts = meta.groupby("task")["task_id"].nunique()
    keep = counts[counts >= 4].index.tolist()
    pi = pi[pi["task"].isin(keep)]
    order = (
        pi.groupby("task")["passed"].mean().mul(100).sort_values(ascending=False).index.tolist()
    )
    models = (
        pd.read_csv(RESULTS / "model_results.csv")
        .query("harness == 'pi'")
        .sort_values("Accuracy (%)", ascending=False)["model_name"]
        .tolist()
    )
    return pi, counts.to_frame("n"), order, models


def task_type_model_means(pi: pd.DataFrame) -> pd.Series:
    return (
        pi.groupby(["model_name", "task"])["passed"]
        .mean()
        .mul(100)
        .groupby("task")
        .mean()
    )


def plot_task_type_bar() -> None:
    pi, counts, order, _ = task_summary()
    summary = task_type_model_means(pi).reindex(order)
    n = counts.loc[order, "n"].astype(int)

    fig, ax = plt.subplots(figsize=(7.8, 4.0))
    y = np.arange(len(order))
    cmap = LinearSegmentedColormap.from_list("task_rank", [TEAL_LIGHT, CREAM, "#DCA96A"])
    colors = [cmap(i / max(1, len(order) - 1)) for i in range(len(order))]
    ax.barh(y, summary.values, color=colors, edgecolor="#686056", linewidth=0.55, height=0.66)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{task_label(t)}  (n={n[t]})" for t in order])
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel("Pass rate (%)  —  mean across 11 Pi-harness models", fontsize=8)
    ax.set_title("A  Pass rate by task type", loc="left", fontsize=9, fontproperties=SERIF_BOLD)
    style_axis(ax)
    for yi, val in zip(y, summary.values):
        ax.text(
            101.2,
            yi,
            f"{val:.0f}%",
            fontsize=6.5,
            va="center",
            ha="left",
            bbox=dict(boxstyle="round,pad=0.16", fc=CREAM_LIGHT, ec="#D8CDBB", lw=0.45),
            clip_on=False,
        )
    save(fig, "fig2_by_task_type")


def plot_task_heatmap() -> None:
    pi, counts, order, models = task_summary()
    mat = (
        pi.groupby(["model_name", "task"])["passed"]
        .mean()
        .mul(100)
        .unstack("task")
        .reindex(index=models, columns=order)
    )

    fig, ax = plt.subplots(figsize=(8.2, 4.35))
    cmap = LinearSegmentedColormap.from_list("txbench_heat", ["#C77442", "#F1DDA8", "#EDEBE3", "#7FC2B5", TEAL])
    im = ax.imshow(mat.values, aspect="auto", cmap=cmap, vmin=0, vmax=100)
    ax.set_yticks(np.arange(len(models)))
    ax.set_yticklabels([model_label(m) for m in models], fontsize=7)
    ax.set_xticks(np.arange(len(order)))
    ax.set_xticklabels([f"{task_label(t)} (n={int(counts.loc[t, 'n'])})" for t in order], rotation=38, ha="right", fontsize=6.5)
    ax.set_title("A  Pass rate by model and task type", loc="left", fontsize=9, fontproperties=SERIF_BOLD)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(length=0)
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            val = mat.iat[i, j]
            ax.text(j, i, f"{val:.0f}", ha="center", va="center", fontsize=5.6, color="white" if val >= 82 else "#121417")
    cbar = fig.colorbar(im, ax=ax, fraction=0.024, pad=0.03)
    cbar.set_label("Pass rate (%)", fontsize=7)
    cbar.ax.tick_params(labelsize=6.5)
    save(fig, "fig2c_by_task_type_heatmap")


def pareto(points: pd.DataFrame, x_col: str, y_col: str) -> pd.DataFrame:
    frontier = []
    best = -np.inf
    for _, row in points.sort_values(x_col).iterrows():
        if row[y_col] > best:
            frontier.append(row)
            best = row[y_col]
    return pd.DataFrame(frontier)


def annotate(ax: plt.Axes, x: float, y: float, text: str, dx: float, dy: float) -> None:
    ax.annotate(
        text,
        xy=(x, y),
        xytext=(dx, dy),
        textcoords="offset points",
        fontsize=6.2,
        ha="left" if dx >= 0 else "right",
        va="center",
        arrowprops=dict(arrowstyle="-", color=AXIS, lw=0.45, shrinkA=2, shrinkB=2),
    )


def plot_cost_frontier() -> None:
    model_results = pd.read_csv(RESULTS / "model_results.csv")
    steps = pd.read_csv(RESULTS / "model_steps.csv")
    df = model_results[model_results["harness"].eq("pi")].merge(
        steps[steps["harness"].eq("pi")][["model_name", "Steps (mean)"]],
        on="model_name",
        how="left",
    )
    df = df.sort_values("Accuracy (%)")

    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(8.8, 3.6), gridspec_kw={"wspace": 0.24})
    for ax, x_col, xlabel in [
        (ax_a, "Cost ($)", "Mean cost per evaluation (USD)"),
        (ax_b, "Steps (mean)", "Mean agent steps per evaluation"),
    ]:
        for _, row in df.iterrows():
            ax.scatter(
                row[x_col],
                row["Accuracy (%)"],
                s=34,
                color=ACCENT,
                edgecolor="white",
                linewidth=0.45,
                zorder=3,
            )
        front = pareto(df, x_col, "Accuracy (%)")
        ax.plot(front[x_col], front["Accuracy (%)"], color=GRAY_DARK, linestyle=(0, (1.8, 2.0)), linewidth=1.0, zorder=2)
        ax.set_ylim(0, 100)
        ax.set_xlabel(xlabel, fontsize=8)
        ax.set_ylabel("Endpoint pass rate (%)", fontsize=8)
        style_axis(ax, xgrid=True)

    ax_a.set_title("A  Accuracy vs. cost", loc="left", fontsize=9, fontproperties=SERIF_BOLD)
    ax_b.set_title("B  Accuracy vs. steps", loc="left", fontsize=9, fontproperties=SERIF_BOLD)

    cost_offsets = {
        "claude-opus-4-8": (-10, 8),
        "gpt-5.5": (-12, 10),
        "gemini-3.5-flash": (8, -8),
        "gpt-5.4": (4, 8),
        "claude-opus-4-7": (8, -10),
        "claude-opus-4-6": (8, -8),
        "gemini-3.1-pro-preview": (10, -11),
        "claude-sonnet-4-6": (-14, -10),
        "kimi-k2p6": (-8, -12),
        "grok-4.20-0309-reasoning": (8, -8),
        "grok-4.3": (6, 8),
    }
    step_offsets = {
        "claude-opus-4-8": (6, 8),
        "gpt-5.5": (8, -8),
        "gemini-3.5-flash": (8, 2),
        "gpt-5.4": (8, 7),
        "claude-opus-4-7": (8, -10),
        "claude-opus-4-6": (7, -8),
        "gemini-3.1-pro-preview": (8, 6),
        "claude-sonnet-4-6": (-14, -10),
        "kimi-k2p6": (8, -12),
        "grok-4.20-0309-reasoning": (8, -10),
        "grok-4.3": (8, 8),
    }
    for _, row in df.iterrows():
        annotate(ax_a, row["Cost ($)"], row["Accuracy (%)"], model_label(row["model_name"]), *cost_offsets[row["model_name"]])
        annotate(ax_b, row["Steps (mean)"], row["Accuracy (%)"], model_label(row["model_name"]), *step_offsets[row["model_name"]])

    handle = plt.Line2D([0], [0], color=GRAY_DARK, linestyle=(0, (1.8, 2.0)), lw=1.0, label="Pareto frontier")
    ax_a.legend(handles=[handle], frameon=False, fontsize=6.8, loc="lower right")
    ax_b.legend(handles=[handle], frameon=False, fontsize=6.8, loc="lower right")
    save(fig, "fig5_cost_frontier")


def main() -> None:
    plot_model_performance()
    plot_task_type_bar()
    plot_task_heatmap()
    plot_cost_frontier()


if __name__ == "__main__":
    main()
