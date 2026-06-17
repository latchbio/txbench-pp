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
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "paper" / "figures"
RESULTS = ROOT.parent / "txbench_internal" / "results"
EVALS = ROOT.parent / "txbench_internal" / "evals"

TEXT = "#15191F"
MUTED = "#5F6872"
GRID = "#D9DEE5"
AXIS = "#AFA89B"
LINE = "#DDD7CB"
CREAM = "#EEE8DC"
CREAM_LIGHT = "#F8F5EE"
ACCENT = "#A95F3D"
ACCENT_LIGHT = "#C97745"
TEAL = "#2A9D8F"
TEAL_DARK = "#19736A"
TEAL_LIGHT = "#A9CEC4"
VIOLET = "#7267C8"
GOLD = "#B89142"
RED = "#D14B4B"
GRAY = "#B8B2AA"
GRAY_DARK = "#8D867E"

SERIF_STACK = ["DejaVu Serif", "serif"]
SERIF = FontProperties(family=SERIF_STACK)
SERIF_BOLD = FontProperties(family=SERIF_STACK, weight="bold")
MONO = FontProperties(family=["DejaVu Sans Mono", "monospace"])
MONO_BOLD = FontProperties(family=["DejaVu Sans Mono", "monospace"], weight="bold")

HARNESS_COLORS = {
    "pi": ACCENT,
    "claude-code": TEAL,
    "openai-codex": VIOLET,
}

HEATMAP = LinearSegmentedColormap.from_list(
    "txbench_heat",
    [ACCENT_LIGHT, "#DDA96D", CREAM_LIGHT, TEAL_LIGHT, TEAL],
)

STAGE_ORDER = [
    "S2_screening_hit_confirmation",
    "S3_drug_response_pharmacogenomics",
    "S5_causal_target_validation",
    "S6_moa_pharmacodynamics",
    "S7_compound_target_engagement",
    "S8_developability_safety",
    "S9_translational_efficacy",
]

PROGRAM_TASKS = [
    "txbx_org_program_ti_exposure_gonogo",
    "H2_toxfree_advance_image",
    "HAI2027_FIG1_COMBO02_single_agent_explained_models",
    "HAI2027_FIG1_DEV01_priority_models",
    "HAI2027_FIG1_DUR01_long_term_supported_models",
    "HAI2027_FIG1_GATE01_decision_gate_models",
]

PROGRAM_LABELS = {
    "txbx_org_program_ti_exposure_gonogo": "Organoid\ngo/no-go",
    "H2_toxfree_advance_image": "Safety\nno-go",
    "HAI2027_FIG1_COMBO02_single_agent_explained_models": "Single-agent\nset",
    "HAI2027_FIG1_DEV01_priority_models": "Priority\nset",
    "HAI2027_FIG1_DUR01_long_term_supported_models": "Long-term\nset",
    "HAI2027_FIG1_GATE01_decision_gate_models": "Decision-gate\nset",
}

DETERMINATE_TASKS = {
    "exposure_pk",
    "biomarker_discovery",
    "safety_assessment",
    "target_engagement",
}

SELECTION_TASKS = {
    "target_dependency",
    "differential_response",
    "hit_prioritization",
    "cheminformatics",
}

plt.rcParams.update(
    {
        "font.family": SERIF_STACK,
        "font.serif": SERIF_STACK,
        "font.size": 8.0,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "savefig.edgecolor": "white",
        "axes.edgecolor": AXIS,
        "axes.labelcolor": TEXT,
        "axes.titlecolor": TEXT,
        "xtick.color": MUTED,
        "ytick.color": TEXT,
        "text.color": TEXT,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
    }
)


def save(fig: plt.Figure, stem: str) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png", "svg"):
        path = FIGURES / f"{stem}.{ext}"
        fig.savefig(path, dpi=520, bbox_inches="tight")
        if ext == "svg":
            text = path.read_text()
            path.write_text("\n".join(line.rstrip() for line in text.splitlines()) + "\n")
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


def stage_axis_label(stage: str, n: int) -> str:
    labels = {
        "S2_screening_hit_confirmation": "S2\nScreen/QC",
        "S3_drug_response_pharmacogenomics": "S3\nDrug resp.",
        "S5_causal_target_validation": "S5\nTarget val.",
        "S6_moa_pharmacodynamics": "S6\nMoA / PD",
        "S7_compound_target_engagement": "S7\nEngage.",
        "S8_developability_safety": "S8\nSafety / PK",
        "S9_translational_efficacy": "S9\nTranslational",
    }
    return f"{labels.get(stage, stage)}\nn={n}"


def stage_label(stage: str, *, short: bool = False) -> str:
    labels = {
        "S2_screening_hit_confirmation": ("S2", "Screening / QC"),
        "S3_drug_response_pharmacogenomics": ("S3", "Drug response"),
        "S5_causal_target_validation": ("S5", "Target validation"),
        "S6_moa_pharmacodynamics": ("S6", "MoA / PD"),
        "S7_compound_target_engagement": ("S7", "Target engagement"),
        "S8_developability_safety": ("S8", "Safety / PK"),
        "S9_translational_efficacy": ("S9", "Translational efficacy"),
    }
    code, name = labels.get(stage, (stage.split("_", 1)[0], stage.replace("_", " ")))
    return f"{code}\n{name}" if short else f"{code}  {name}"


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


def read_results_with_meta() -> pd.DataFrame:
    raw = pd.read_csv(RESULTS / "results_table.csv")
    raw["passed"] = raw["passed"].astype(bool)
    meta = load_metadata()
    return raw.merge(meta[["task_id", "tx_stage", "task", "kit"]], on="task_id", how="left")


def style_axis(ax: plt.Axes, *, xgrid: bool = True, ygrid: bool = False) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(AXIS)
    ax.spines["bottom"].set_color(AXIS)
    ax.tick_params(axis="both", labelsize=7.2)
    if xgrid:
        ax.grid(axis="x", color=GRID, linewidth=0.55, alpha=0.95)
    if ygrid:
        ax.grid(axis="y", color=GRID, linewidth=0.55, alpha=0.75)
    ax.set_axisbelow(True)


def heat_text_color(value: float) -> str:
    return "white" if value <= 18 or value >= 82 else TEXT


def plot_model_performance() -> None:
    model_results = pd.read_csv(RESULTS / "model_results.csv")
    raw = pd.read_csv(RESULTS / "results_table.csv")
    raw["passed"] = raw["passed"].astype(bool)

    ordered = model_results.sort_values("Accuracy (%)", ascending=False).reset_index(drop=True)
    pi_order = (
        model_results[model_results["harness"].eq("pi")]
        .sort_values("Accuracy (%)", ascending=False)["model_name"]
        .tolist()
    )

    fig, (ax_a, ax_b) = plt.subplots(
        1,
        2,
        figsize=(9.8, 4.85),
        gridspec_kw={"width_ratios": [1.16, 0.96], "wspace": 0.34},
    )

    y = np.arange(len(ordered))
    markers = {"pi": "o", "claude-code": "s", "openai-codex": "D"}
    for yi, row in ordered.iterrows():
        harness = row["harness"]
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
            markersize=4.4,
            elinewidth=0.9,
            capsize=2.1,
            capthick=0.75,
            zorder=3,
        )
        ax_a.text(
            min(row["ci_upper"] + 1.1, 70.7),
            yi,
            f"{acc:.1f}%",
            fontsize=5.9,
            va="center",
            ha="left",
            color=color,
            fontproperties=MONO_BOLD,
            clip_on=False,
        )

    config_labels = [
        f"{model_label(r.model_name)} / {harness_label(r.harness)}"
        for r in ordered.itertuples()
    ]
    ax_a.set_yticks(y)
    ax_a.set_yticklabels(config_labels, fontsize=6.4)
    ax_a.set_ylim(len(ordered) - 0.35, -0.65)
    ax_a.set_xlim(0, 72)
    ax_a.set_xlabel("Endpoint pass rate (%)", fontsize=8)
    ax_a.set_title("A  Model-harness pass rate", loc="left", fontsize=9, fontproperties=SERIF_BOLD)
    style_axis(ax_a)
    handles = [
        Line2D(
            [0],
            [0],
            marker=markers[h],
            color="none",
            markerfacecolor=HARNESS_COLORS[h],
            markeredgecolor=HARNESS_COLORS[h],
            markersize=5,
            label=harness_label(h),
        )
        for h in ["pi", "claude-code", "openai-codex"]
    ]
    ax_a.legend(handles=handles, frameon=False, fontsize=6.6, loc="lower right", title="Harness", title_fontsize=6.6)

    reliability = []
    pi = raw[raw["harness"].eq("pi")]
    for model in pi_order:
        by_task = pi[pi["model_name"].eq(model)].groupby("task_id")["passed"].sum()
        counts = by_task.value_counts().reindex([0, 1, 2, 3], fill_value=0).astype(int)
        reliability.append(counts)
    rel = pd.DataFrame(reliability, index=pi_order)
    colors = [CREAM, GRAY, TEAL_LIGHT, ACCENT_LIGHT]
    labels = ["0 passed", "1 passed", "2 passed", "3 passed"]
    y2 = np.arange(len(pi_order))
    left = np.zeros(len(pi_order))
    for i, col in enumerate([0, 1, 2, 3]):
        vals = rel[col].to_numpy()
        ax_b.barh(
            y2,
            vals,
            left=left,
            height=0.64,
            color=colors[i],
            edgecolor="white",
            linewidth=0.45,
            label=labels[i],
        )
        for yi, v, lft in zip(y2, vals, left):
            if v >= 8:
                ax_b.text(
                    lft + v / 2,
                    yi,
                    str(int(v)),
                    ha="center",
                    va="center",
                    fontsize=5.8,
                    color=TEXT if i < 3 else "white",
                    fontproperties=MONO_BOLD,
                )
        left += vals
    ax_b.set_yticks(y2)
    ax_b.set_yticklabels([model_label(m) for m in pi_order], fontsize=6.4)
    ax_b.set_ylim(len(pi_order) - 0.35, -0.65)
    ax_b.set_xlim(0, 100)
    ax_b.set_xlabel("Evaluations (n = 100)", fontsize=8)
    ax_b.set_title("B  Repeatability across three Pi attempts", loc="left", fontsize=9, fontproperties=SERIF_BOLD)
    style_axis(ax_b)
    ax_b.legend(frameon=False, fontsize=6.2, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.15), handlelength=1.2, columnspacing=1.0)

    save(fig, "model_performance")


def task_summary() -> tuple[pd.DataFrame, pd.DataFrame, list[str], list[str]]:
    meta = load_metadata()
    df = read_results_with_meta()
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


def plot_task_type_by_model() -> None:
    pi, counts, order, models = task_summary()
    mat = (
        pi.groupby(["task", "model_name"])["passed"]
        .mean()
        .mul(100)
        .unstack("model_name")
        .reindex(index=order, columns=models)
    )

    fig, ax = plt.subplots(figsize=(9.25, 4.85))
    xx, yy = np.meshgrid(np.arange(len(models)), np.arange(len(order)))
    vals = mat.values.astype(float)
    sc = ax.scatter(
        xx.ravel(),
        yy.ravel(),
        s=22 + vals.ravel() * 1.05,
        c=vals.ravel(),
        cmap=HEATMAP,
        vmin=0,
        vmax=100,
        edgecolor="white",
        linewidth=0.45,
        zorder=3,
    )

    ax.set_xlim(-0.55, len(models) - 0.45)
    ax.set_ylim(len(order) - 0.5, -0.5)
    ax.set_xticks(np.arange(len(models)))
    ax.set_xticklabels([model_label(m) for m in models], rotation=34, ha="right", fontsize=6.2)
    ax.set_yticks(np.arange(len(order)))
    ax.set_yticklabels([f"{task_label(t)}  (n={int(counts.loc[t, 'n'])})" for t in order], fontsize=6.6)
    ax.set_xlabel("Pi-harness model", fontsize=7.6)
    ax.set_title("Pass rate by task type and model", loc="left", fontsize=9, fontproperties=SERIF_BOLD)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(length=0)
    ax.set_xticks(np.arange(-0.5, len(models), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(order), 1), minor=True)
    ax.grid(which="minor", color=GRID, linewidth=0.35, alpha=0.65)
    ax.tick_params(which="minor", bottom=False, left=False)
    cbar = fig.colorbar(sc, ax=ax, fraction=0.024, pad=0.022)
    cbar.set_label("Pass rate (%)", fontsize=7)
    cbar.ax.tick_params(labelsize=6.2)

    save(fig, "fig2_by_task_type")


def plot_failure_taxonomy() -> None:
    raw = pd.read_csv(RESULTS / "results_table.csv")
    raw["passed"] = raw["passed"].astype(bool)
    model_results = pd.read_csv(RESULTS / "model_results.csv")
    pi_accuracy = (
        model_results[model_results["harness"] == "pi"]
        .set_index("model_name")["Accuracy (%)"]
        .to_dict()
    )
    failing_steps = (
        raw[(raw["harness"] == "pi") & (~raw["passed"])]
        .groupby("model_name")
        .agg(mean_steps=("steps", "mean"), n_fail=("steps", "size"))
        .reset_index()
        .sort_values("mean_steps", ascending=True)
    )

    scientific = [
        ("Method errors", 40, TEAL),
        ("Calibration", 31, ACCENT),
        ("Perception", 10, GRAY_DARK),
        ("Prior over data", 10, ACCENT_LIGHT),
        ("Over-reading", 10, VIOLET),
    ]
    behavior = [
        ("Engaged, analytically wrong", 67, GRAY_DARK),
        ("Abandoned-correct", 12, ACCENT_LIGHT),
        ("Weak commitment", 9, MUTED),
        ("Memorized literature", 6, ACCENT),
        ("Under-investment", 6, CREAM),
    ]

    fig = plt.figure(figsize=(8.8, 4.85))
    gs = fig.add_gridspec(
        2,
        2,
        height_ratios=[1.0, 1.08],
        width_ratios=[1.0, 1.08],
        hspace=0.70,
        wspace=0.46,
    )
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, :])

    for ax, rows, title, xlabel in [
        (
            ax_a,
            scientific,
            "A  Scientific error among assignable failures",
            "% of scientific-error failures",
        ),
        (
            ax_b,
            behavior,
            "B  Trajectory behavior among all failures",
            "% of failing trajectories",
        ),
    ]:
        y = np.arange(len(rows))
        vals = [r[1] for r in rows]
        colors = [r[2] for r in rows]
        ax.barh(y, vals, color=colors, edgecolor="none", linewidth=0, height=0.62)
        ax.set_yticks(y)
        ax.set_yticklabels([r[0] for r in rows], fontsize=7.0)
        ax.set_xlim(0, 75 if ax is ax_b else 45)
        ax.set_xlabel(xlabel, fontsize=7.8)
        ax.set_title(title, loc="left", fontsize=9.0, fontproperties=SERIF_BOLD, pad=7)
        style_axis(ax)
        ax.spines["left"].set_visible(False)
        ax.tick_params(axis="y", length=0)
        ax.invert_yaxis()
        for yi, val in enumerate(vals):
            if val >= 25:
                x = val - 1.3
                ha = "right"
                color = "white"
            else:
                x = val + (1.2 if ax is ax_a else 1.5)
                ha = "left"
                color = TEXT
            ax.text(
                x,
                yi,
                f"{val}%",
                va="center",
                ha=ha,
                fontsize=6.4,
                color=color,
                fontproperties=SERIF,
            )

    y = np.arange(len(failing_steps))
    vals = failing_steps["mean_steps"].to_numpy()
    colors = [
        ACCENT if m == "grok-4.3" else TEAL if vals[i] >= 30 else GRAY
        for i, m in enumerate(failing_steps["model_name"])
    ]
    ax_c.barh(y, vals, height=0.58, color=colors, edgecolor="none", linewidth=0)
    ax_c.set_yticks(y)
    ax_c.set_yticklabels([model_label(m) for m in failing_steps["model_name"]], fontsize=6.7)
    ax_c.set_xlim(0, max(vals) + 8)
    ax_c.set_xlabel("Mean steps among failing Pi trajectories", fontsize=7.8)
    ax_c.set_title(
        "C  Failing-trajectory effort by model",
        loc="left",
        fontsize=9.0,
        fontproperties=SERIF_BOLD,
        pad=7,
    )
    style_axis(ax_c)
    ax_c.spines["left"].set_visible(False)
    ax_c.tick_params(axis="y", length=0)
    ax_c.invert_yaxis()
    for yi, row in enumerate(failing_steps.itertuples(index=False)):
        label = (
            f"{row.mean_steps:.1f} steps, "
            f"{pi_accuracy.get(row.model_name, float('nan')):.0f}% pass"
        )
        ax_c.text(
            row.mean_steps + 0.8,
            yi,
            label,
            va="center",
            ha="left",
            fontsize=6.2,
            color=MUTED,
            fontproperties=SERIF,
        )

    save(fig, "fig3_failure_taxonomy_granular")


def plot_task_heatmap() -> None:
    pi, counts, order, models = task_summary()
    mat = (
        pi.groupby(["model_name", "task"])["passed"]
        .mean()
        .mul(100)
        .unstack("task")
        .reindex(index=models, columns=order)
    )

    fig, ax = plt.subplots(figsize=(9.4, 4.85))
    im = ax.imshow(mat.values, aspect="auto", cmap=HEATMAP, vmin=0, vmax=100)
    ax.set_yticks(np.arange(len(models)))
    ax.set_yticklabels([model_label(m) for m in models], fontsize=7.0)
    ax.set_xticks(np.arange(len(order)))
    ax.set_xticklabels(
        [f"{task_label(t)}\nn={int(counts.loc[t, 'n'])}" for t in order],
        rotation=36,
        ha="right",
        fontsize=6.4,
    )
    ax.set_title("Pass rate by model and task type", loc="left", fontsize=9, fontproperties=SERIF_BOLD)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(length=0)
    ax.set_xticks(np.arange(-0.5, mat.shape[1], 1), minor=True)
    ax.set_yticks(np.arange(-0.5, mat.shape[0], 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=0.55)
    ax.tick_params(which="minor", bottom=False, left=False)
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            val = mat.iat[i, j]
            ax.text(
                j,
                i,
                f"{val:.0f}",
                ha="center",
                va="center",
                fontsize=5.5,
                color=heat_text_color(val),
                fontproperties=MONO_BOLD,
            )
    cbar = fig.colorbar(im, ax=ax, fraction=0.022, pad=0.025)
    cbar.set_label("Pass rate (%)", fontsize=7)
    cbar.ax.tick_params(labelsize=6.4)
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
        fontsize=6.1,
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

    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(8.9, 3.65), gridspec_kw={"wspace": 0.28})
    label_models = {
        "claude-opus-4-8",
        "gpt-5.5",
        "gpt-5.4",
        "gemini-3.5-flash",
        "kimi-k2p6",
        "grok-4.20-0309-reasoning",
        "grok-4.3",
    }

    for ax, x_col, xlabel in [
        (ax_a, "Cost ($)", "Mean cost per evaluation (USD)"),
        (ax_b, "Steps (mean)", "Mean agent steps per evaluation"),
    ]:
        front = pareto(df, x_col, "Accuracy (%)")
        frontier_models = set(front["model_name"])
        for _, row in df.iterrows():
            on_frontier = row["model_name"] in frontier_models
            ax.scatter(
                row[x_col],
                row["Accuracy (%)"],
                s=34 if on_frontier else 28,
                color=ACCENT if on_frontier else GRAY_DARK,
                edgecolor="white",
                linewidth=0.45,
                zorder=3,
            )
        ax.plot(
            front[x_col],
            front["Accuracy (%)"],
            color=GRAY_DARK,
            linestyle=(0, (1.8, 2.0)),
            linewidth=1.0,
            zorder=2,
        )
        ax.set_ylim(14, 64)
        ax.set_xlabel(xlabel, fontsize=8)
        ax.set_ylabel("Endpoint pass rate (%)", fontsize=8)
        style_axis(ax, xgrid=True)

    ax_a.set_title("A  Accuracy vs. cost", loc="left", fontsize=9, fontproperties=SERIF_BOLD)
    ax_b.set_title("B  Accuracy vs. steps", loc="left", fontsize=9, fontproperties=SERIF_BOLD)

    cost_offsets = {
        "claude-opus-4-8": (8, 9),
        "gpt-5.5": (-9, 11),
        "gpt-5.4": (8, 8),
        "gemini-3.5-flash": (8, -9),
        "kimi-k2p6": (8, -11),
        "grok-4.20-0309-reasoning": (8, 9),
        "grok-4.3": (8, -8),
    }
    step_offsets = {
        "claude-opus-4-8": (7, 9),
        "gpt-5.5": (8, -9),
        "gpt-5.4": (8, 8),
        "gemini-3.5-flash": (-10, 9),
        "kimi-k2p6": (8, -10),
        "grok-4.20-0309-reasoning": (8, -9),
        "grok-4.3": (8, 8),
    }
    for _, row in df.iterrows():
        if row["model_name"] not in label_models:
            continue
        annotate(ax_a, row["Cost ($)"], row["Accuracy (%)"], model_label(row["model_name"]), *cost_offsets[row["model_name"]])
        annotate(ax_b, row["Steps (mean)"], row["Accuracy (%)"], model_label(row["model_name"]), *step_offsets[row["model_name"]])

    handle = Line2D([0], [0], color=GRAY_DARK, linestyle=(0, (1.8, 2.0)), lw=1.0, label="Pareto frontier")
    ax_a.legend(handles=[handle], frameon=False, fontsize=6.8, loc="lower right")
    ax_b.legend(handles=[handle], frameon=False, fontsize=6.8, loc="lower right")
    save(fig, "fig5_cost_frontier")


def plot_by_stage() -> None:
    df = read_results_with_meta()
    pi = df[df["harness"].eq("pi") & df["tx_stage"].isin(STAGE_ORDER)].copy()
    models = (
        pd.read_csv(RESULTS / "model_results.csv")
        .query("harness == 'pi'")
        .sort_values("Accuracy (%)", ascending=False)["model_name"]
        .tolist()
    )

    stage_counts = pi.groupby("tx_stage")["task_id"].nunique().reindex(STAGE_ORDER)
    mat = (
        pi.groupby(["model_name", "tx_stage"])["passed"]
        .mean()
        .mul(100)
        .unstack("tx_stage")
        .reindex(index=models, columns=STAGE_ORDER)
    )

    fig, ax_b = plt.subplots(figsize=(8.7, 3.35))

    x = np.arange(len(STAGE_ORDER))
    highlights = {
        "claude-opus-4-8": (ACCENT, "Opus 4.8", 1.0),
        "gpt-5.5": (VIOLET, "GPT-5.5", 0.4),
        "gemini-3.5-flash": (TEAL, "Gemini 3.5", -1.2),
    }
    for model in models:
        vals = mat.loc[model].astype(float).values
        if model in highlights:
            color, _, _ = highlights[model]
            ax_b.plot(x, vals, color=color, lw=1.35, alpha=0.95, zorder=3)
            ax_b.scatter(x, vals, s=15, color=color, edgecolor="white", linewidth=0.45, zorder=4)
        else:
            ax_b.plot(x, vals, color="#BEB6AA", lw=0.55, alpha=0.58, zorder=1)
            ax_b.scatter(x, vals, s=7, color="#BEB6AA", edgecolor="none", alpha=0.58, zorder=2)

    endpoint_labels = []
    for model in models:
        vals = mat.loc[model].astype(float).values
        color = highlights.get(model, ("#6D665E", "", 0))[0]
        endpoint_labels.append({"model": model, "target": vals[-1], "color": color})
    endpoint_labels.sort(key=lambda item: item["target"], reverse=True)
    min_gap = 4.2
    y_top = 88.0
    y_bottom = 10.0
    previous = y_top + min_gap
    for item in endpoint_labels:
        item["label_y"] = min(item["target"], previous - min_gap)
        previous = item["label_y"]
    underflow = y_bottom - endpoint_labels[-1]["label_y"]
    if underflow > 0:
        for item in endpoint_labels:
            item["label_y"] += underflow

    for item in endpoint_labels:
        model = item["model"]
        vals = mat.loc[model].astype(float).values
        color = item["color"]
        label_x = x[-1] + 0.25
        ax_b.plot([x[-1] + 0.03, label_x - 0.04], [vals[-1], item["label_y"]], color=color, lw=0.35, alpha=0.72, zorder=2)
        ax_b.text(
            label_x,
            item["label_y"],
            model_label(model),
            ha="left",
            va="center",
            fontsize=5.05,
            fontproperties=SERIF_BOLD if model in highlights else SERIF,
            color=color,
        )

    ax_b.set_xlim(-0.25, len(STAGE_ORDER) + 1.26)
    ax_b.set_ylim(0, 94)
    ax_b.set_xticks(x)
    ax_b.set_xticklabels(
        [stage_axis_label(s, int(stage_counts[s])) for s in STAGE_ORDER],
        rotation=0,
        fontsize=6.2,
    )
    ax_b.set_xlabel("Program stage", fontsize=7.5)
    ax_b.set_ylabel("Endpoint pass rate (%)", fontsize=7.5)
    ax_b.set_title("Pass rate by program stage", loc="left", fontsize=9, fontproperties=SERIF_BOLD)
    style_axis(ax_b, xgrid=False, ygrid=True)
    ax_b.spines["left"].set_visible(False)
    ax_b.tick_params(axis="y", labelsize=6.6, length=0)
    ax_b.tick_params(axis="x", length=0, pad=2)

    save(fig, "fig_by_stage")


def plot_program_model_compare() -> None:
    raw = pd.read_csv(RESULTS / "results_table.csv")
    raw["passed"] = raw["passed"].astype(bool)
    pi = raw[raw["harness"].eq("pi") & raw["task_id"].isin(PROGRAM_TASKS)].copy()
    overall = (
        pd.read_csv(RESULTS / "model_results.csv")
        .query("harness == 'pi'")
        .set_index("model_name")["Accuracy (%)"]
    )
    prog = pi.groupby("model_name")["passed"].agg(["mean", "sum", "count"])
    prog["program_rate"] = prog["mean"] * 100
    prog["overall"] = overall.reindex(prog.index)
    order = prog.sort_values(["program_rate", "overall"], ascending=[False, False]).index.tolist()
    mat = (
        pi.groupby(["model_name", "task_id"])["passed"]
        .mean()
        .mul(100)
        .unstack("task_id")
        .reindex(index=order, columns=PROGRAM_TASKS)
    )

    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(9.6, 4.45), gridspec_kw={"width_ratios": [0.86, 1.14], "wspace": 0.30})
    y = np.arange(len(order))
    for yi, model in enumerate(order):
        o = prog.loc[model, "overall"]
        p = prog.loc[model, "program_rate"]
        line_color = TEAL if p >= o else ACCENT_LIGHT
        ax_a.plot([o, p], [yi, yi], color=line_color, lw=1.25, alpha=0.9, zorder=1)
        ax_a.scatter(o, yi, s=25, color=GRAY_DARK, edgecolor="white", linewidth=0.45, zorder=3)
        ax_a.scatter(p, yi, s=30, color=line_color, edgecolor="white", linewidth=0.45, zorder=4)
        ax_a.text(
            106.0,
            yi,
            f"{p:.0f}%",
            ha="right",
            va="center",
            fontsize=5.8,
            color=line_color,
            fontproperties=SERIF_BOLD,
        )
    ax_a.set_yticks(y)
    ax_a.set_yticklabels([model_label(m) for m in order], fontsize=6.6)
    ax_a.set_ylim(len(order) - 0.35, -0.65)
    ax_a.set_xlim(0, 110)
    ax_a.set_xlabel("Pass rate (%)", fontsize=8)
    ax_a.set_title("A  Overall vs. program decisions", loc="left", fontsize=9, fontproperties=SERIF_BOLD)
    style_axis(ax_a)
    ax_a.text(
        0.03,
        0.98,
        "Spearman rho = 0.08",
        transform=ax_a.transAxes,
        fontsize=6.0,
        color=MUTED,
        ha="left",
        va="top",
    )
    ax_a.text(
        106.0,
        -0.58,
        "Program",
        fontsize=5.8,
        color=MUTED,
        ha="right",
        va="bottom",
        fontproperties=SERIF_BOLD,
    )
    im = ax_b.imshow(mat.values, aspect="auto", cmap=HEATMAP, vmin=0, vmax=100)
    ax_b.set_yticks(np.arange(len(order)))
    ax_b.set_yticklabels([model_label(m) for m in order], fontsize=6.4)
    ax_b.set_xticks(np.arange(len(PROGRAM_TASKS)))
    ax_b.set_xticklabels([PROGRAM_LABELS[t] for t in PROGRAM_TASKS], rotation=34, ha="right", fontsize=6.0)
    ax_b.set_title("B  Per-decision pass rate", loc="left", fontsize=9, fontproperties=SERIF_BOLD)
    for spine in ax_b.spines.values():
        spine.set_visible(False)
    ax_b.tick_params(length=0)
    ax_b.set_xticks(np.arange(-0.5, mat.shape[1], 1), minor=True)
    ax_b.set_yticks(np.arange(-0.5, mat.shape[0], 1), minor=True)
    ax_b.grid(which="minor", color="white", linewidth=0.55)
    ax_b.tick_params(which="minor", bottom=False, left=False)
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            val = mat.iat[i, j]
            ax_b.text(j, i, f"{val:.0f}", ha="center", va="center", fontsize=5.3, color=heat_text_color(val), fontproperties=MONO_BOLD)
    cbar = fig.colorbar(im, ax=ax_b, fraction=0.025, pad=0.025)
    cbar.set_label("Pass rate (%)", fontsize=7)
    cbar.ax.tick_params(labelsize=6.4)
    save(fig, "fig_program_model_compare")


def plot_harness_impact() -> None:
    model_results = pd.read_csv(RESULTS / "model_results.csv")
    pivot = model_results.pivot(index="model_name", columns="harness", values="Accuracy (%)")
    indexed = model_results.set_index(["model_name", "harness"])
    pair_rows = []
    for model in ["claude-opus-4-8", "claude-opus-4-7", "claude-opus-4-6"]:
        pair_rows.append((model, "claude-code", pivot.loc[model, "claude-code"], pivot.loc[model, "pi"]))
    for model in ["gpt-5.5", "gpt-5.4"]:
        pair_rows.append((model, "openai-codex", pivot.loc[model, "openai-codex"], pivot.loc[model, "pi"]))

    fig, ax = plt.subplots(figsize=(7.6, 2.55))
    y = np.arange(len(pair_rows))
    offset = 0.13
    for yi, (model, alt_harness, alt, pi) in enumerate(pair_rows):
        ax.plot([alt, pi], [yi - offset, yi + offset], color=LINE, lw=0.75, zorder=1)
        for harness, acc, marker, pos_y in [
            (alt_harness, alt, "s" if alt_harness == "claude-code" else "D", yi - offset),
            ("pi", pi, "o", yi + offset),
        ]:
            row = indexed.loc[(model, harness)]
            lo = acc - row["ci_lower"]
            hi = row["ci_upper"] - acc
            color = HARNESS_COLORS[harness]
            ax.errorbar(
                acc,
                pos_y,
                xerr=np.array([[lo], [hi]]),
                fmt=marker,
                color=color,
                ecolor=color,
                markersize=4.4,
                elinewidth=0.9,
                capsize=2.0,
                capthick=0.75,
                zorder=3,
            )
        ax.text(
            69.5,
            yi,
            f"+{pi - alt:.1f} pp",
            fontsize=6.1,
            va="center",
            ha="left",
            color=ACCENT,
            fontproperties=SERIF_BOLD,
        )

    ax.set_yticks(y)
    ax.set_yticklabels([model_label(m) for m, _, _, _ in pair_rows], fontsize=6.8)
    ax.set_ylim(len(pair_rows) - 0.35, -0.65)
    ax.set_xlim(30, 75)
    ax.set_xlabel("Endpoint pass rate (%)", fontsize=8)
    ax.set_title("Score difference across harnesses", loc="left", fontsize=9, fontproperties=SERIF_BOLD)
    style_axis(ax)
    ax.text(
        69.5,
        -0.58,
        "Pi advantage",
        fontsize=5.8,
        va="bottom",
        ha="left",
        color=MUTED,
        fontproperties=SERIF_BOLD,
    )
    ax.legend(
        handles=[
            Line2D([0], [0], marker="o", color="none", markerfacecolor=ACCENT, markeredgecolor=ACCENT, markersize=6, label="Pi"),
            Line2D([0], [0], marker="s", color="none", markerfacecolor=TEAL, markeredgecolor=TEAL, markersize=6, label="Claude Code"),
            Line2D([0], [0], marker="D", color="none", markerfacecolor=VIOLET, markeredgecolor=VIOLET, markersize=5.5, label="Codex"),
        ],
        frameon=False,
        fontsize=6.3,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.18),
        ncol=3,
        columnspacing=0.9,
        handletextpad=0.35,
    )
    save(fig, "fig_harness_impact")


def main() -> None:
    plot_model_performance()
    plot_failure_taxonomy()
    plot_by_stage()
    plot_task_type_by_model()
    plot_task_heatmap()
    plot_cost_frontier()
    plot_program_model_compare()
    plot_harness_impact()


if __name__ == "__main__":
    main()
