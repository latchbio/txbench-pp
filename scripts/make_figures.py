#!/usr/bin/env python3
"""Generate TxBench-PP paper template figures."""
from __future__ import annotations

import os
import textwrap
import csv
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-cache")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "paper" / "figures"
INTERNAL_RESULTS = ROOT.parent / "txbench_internal" / "results" / "model_results.csv"

TEXT = "#15191F"
MUTED = "#5F6872"
GRID = "#D9DEE5"
AXIS = "#AFA89B"
LINE = "#DDD7CB"
ACCENT = "#A95F3D"
ACCENT_LIGHT = "#C97745"
TEAL = "#2A9D8F"
VIOLET = "#7267C8"
GOLD = "#B89142"
RED = "#D14B4B"
GRAY = "#B8B2AA"
GRAY_DARK = "#8D867E"
CREAM = "#FBFAF6"
WHITE = "#FFFFFF"

DEFAULT_MODEL_RESULTS = [
    ("claude-opus-4-8", "pi", 59.33, 51.05, 67.61, 1.5695),
    ("gpt-5.5", "pi", 55.33, 47.02, 63.65, 1.0556),
    ("claude-opus-4-8", "claude-code", 54.67, 45.92, 63.41, 1.8494),
    ("gemini-3.5-flash", "pi", 51.33, 42.90, 59.76, 1.2680),
    ("gpt-5.4", "pi", 49.67, 41.28, 58.05, 0.7790),
    ("claude-opus-4-7", "pi", 49.33, 40.39, 58.28, 1.0023),
    ("gpt-5.5", "openai-codex", 47.33, 39.57, 55.10, 1.0222),
    ("gpt-5.4", "openai-codex", 46.67, 38.80, 54.53, 0.8295),
    ("claude-opus-4-6", "pi", 44.67, 36.14, 53.19, 0.7445),
    ("claude-opus-4-7", "claude-code", 44.00, 35.92, 52.08, 1.1308),
    ("claude-opus-4-6", "claude-code", 41.33, 32.92, 49.75, 0.7552),
    ("gemini-3.1-pro-preview", "pi", 40.00, 31.54, 48.46, 0.6057),
    ("claude-sonnet-4-6", "pi", 36.00, 28.44, 43.56, 0.5443),
    ("kimi-k2p6", "pi", 29.67, 22.33, 37.00, 0.3912),
    ("grok-4.20-0309-reasoning", "pi", 19.67, 13.42, 25.91, 0.1065),
    ("grok-4.3", "pi", 18.33, 11.86, 24.80, 0.0243),
]

HARNESS_COLORS = {
    "pi": ACCENT,
    "claude-code": TEAL,
    "openai-codex": VIOLET,
}

SERIF_STACK = ["DejaVu Serif", "serif"]
MONO_STACK = ["DejaVu Sans Mono", "monospace"]
SERIF = FontProperties(family=SERIF_STACK)
SERIF_BOLD = FontProperties(family=SERIF_STACK, weight="bold")
MONO = FontProperties(family=MONO_STACK)
MONO_BOLD = FontProperties(family=MONO_STACK, weight="bold")

plt.rcParams.update(
    {
        "font.family": SERIF_STACK,
        "font.serif": SERIF_STACK,
        "font.monospace": MONO_STACK,
        "font.size": 8.0,
        "figure.facecolor": WHITE,
        "axes.facecolor": WHITE,
        "savefig.facecolor": WHITE,
        "savefig.edgecolor": WHITE,
        "axes.edgecolor": AXIS,
        "axes.labelcolor": TEXT,
        "axes.titlecolor": TEXT,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "text.color": TEXT,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
    }
)


def save(fig: plt.Figure, stem: str) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png", "svg"):
        fig.savefig(FIGURES / f"{stem}.{ext}", dpi=520, bbox_inches="tight")
    plt.close(fig)
    print(f"saved {stem}")


def wrap(text: str, width: int) -> str:
    return "\n".join(textwrap.wrap(text, width=width, break_long_words=False))


def rounded_box(
    ax: plt.Axes,
    xy: tuple[float, float],
    w: float,
    h: float,
    *,
    fc: str,
    ec: str = LINE,
    lw: float = 0.7,
    radius: float = 0.035,
    z: int = 1,
) -> FancyBboxPatch:
    patch = FancyBboxPatch(
        xy,
        w,
        h,
        boxstyle=f"round,pad=0.008,rounding_size={radius}",
        facecolor=fc,
        edgecolor=ec,
        linewidth=lw,
        zorder=z,
    )
    ax.add_patch(patch)
    return patch


def label(ax: plt.Axes, x: float, y: float, text: str, *, size=8, color=TEXT, bold=False, ha="left", va="center", mono=False):
    ax.text(
        x,
        y,
        text,
        fontsize=size,
        color=color,
        fontproperties=MONO_BOLD if mono and bold else MONO if mono else SERIF_BOLD if bold else SERIF,
        ha=ha,
        va=va,
    )


def load_model_results() -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    if INTERNAL_RESULTS.exists():
        with INTERNAL_RESULTS.open(newline="") as f:
            for row in csv.DictReader(f):
                rows.append(
                    {
                        "model": row["model_name"],
                        "harness": row["harness"],
                        "acc": float(row["Accuracy (%)"]),
                        "ci_low": float(row["ci_lower"]),
                        "ci_high": float(row["ci_upper"]),
                        "cost": float(row["Cost ($)"]),
                    }
                )
    else:
        rows = [
            {
                "model": model,
                "harness": harness,
                "acc": acc,
                "ci_low": lo,
                "ci_high": hi,
                "cost": cost,
            }
            for model, harness, acc, lo, hi, cost in DEFAULT_MODEL_RESULTS
        ]
    return rows


def model_label(model: str) -> str:
    names = {
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
    return names.get(model, model)


def draw_scope_panel(ax: plt.Axes) -> None:
    columns = ["Discovery", "Development", "Translation"]
    rows = [
        (
            "Small\nmolecule",
            [
                ("HTS / QC\nDRC + target validation\nMoA + selectivity", ACCENT),
                ("ADMET / DMPK\nPK/PD + exposure\nSafety + coverage", TEAL),
                ("Disease-model efficacy\nTherapeutic index\nAdvance / kill", RED),
            ],
            "current",
        ),
        (
            "Biologic",
            [
                ("Affinity maturation\nBinding kinetics\nFunctional assays", GRAY),
                ("FcRn / PK\nStability + viscosity\nEffector function", GRAY),
                ("NHP PK / tox\nADA + cytokines\nHuman dose", GRAY),
            ],
            "future",
        ),
        (
            "Oligo",
            [
                ("Guide screen\nKnockdown\nOff-targets", GRAY),
                ("Delivery vehicle\nTissue distribution\nDuration", GRAY),
                ("NHP PK / tox\nImmunogenicity\nHuman dose", GRAY),
            ],
            "future",
        ),
    ]
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    label(ax, 0.010, 0.945, "A", size=9.5, bold=True, mono=True, color=ACCENT)
    label(ax, 0.055, 0.945, "TxBench-PP covers selected small-molecule preclinical decisions", size=9.3, bold=True)

    left = 0.225
    cell_w = 0.225
    cell_h = 0.132
    col_gap = 0.022
    row_gap = 0.040
    row0_y = 0.535
    for j, head in enumerate(columns):
        x = left + j * (cell_w + col_gap)
        rounded_box(ax, (x, 0.735), cell_w, 0.075, fc=CREAM, ec=LINE, lw=0.45, radius=0.012)
        label(ax, x + cell_w / 2, 0.772, head, size=7.7, bold=True, ha="center")

    # Mark the currently benchmarked slice while keeping the full map visible.
    scope_x = left - 0.018
    scope_y = row0_y - 0.022
    scope_w = 3 * cell_w + 2 * col_gap + 0.036
    scope_h = cell_h + 0.044
    ax.add_patch(
        FancyBboxPatch(
            (scope_x, scope_y),
            scope_w,
            scope_h,
            boxstyle="round,pad=0.008,rounding_size=0.018",
            facecolor="none",
            edgecolor=ACCENT,
            linewidth=1.1,
            linestyle=(0, (1.1, 2.0)),
            zorder=4,
        )
    )
    for i, (row_name, cells, tag) in enumerate(rows):
        y = row0_y - i * (cell_h + row_gap)
        label(ax, 0.050, y + cell_h * 0.52, row_name, size=7.05, bold=True, ha="left")
        for j, (txt, c) in enumerate(cells):
            x = left + j * (cell_w + col_gap)
            fc = "#F8F3ED" if tag == "current" else "#F0EEE9"
            ec = c if tag == "current" else LINE
            rounded_box(ax, (x, y), cell_w, cell_h, fc=fc, ec=ec, lw=0.75 if tag == "current" else 0.55, radius=0.016)
            rounded_box(ax, (x + 0.012, y + 0.022), 0.024, cell_h - 0.044, fc=c if tag == "current" else GRAY, ec="none", radius=0.006)
            label(
                ax,
                x + 0.052,
                y + cell_h / 2,
                txt,
                size=5.55 if tag == "current" else 5.25,
                color=TEXT if tag == "current" else MUTED,
                bold=tag == "current",
                ha="left",
            )

    label(
        ax,
        left,
        0.060,
        "Current release: small-molecule preclinical pharmacology task groups. Future: other modalities and full program stories.",
        size=5.2,
        color=MUTED,
    )


def draw_passrate_panel(ax: plt.Axes, rows: list[dict[str, float | str]]) -> None:
    rows = sorted(rows, key=lambda r: float(r["acc"]), reverse=True)
    y = list(range(len(rows)))
    colors = [HARNESS_COLORS.get(str(r["harness"]), GRAY_DARK) for r in rows]
    acc = [float(r["acc"]) for r in rows]
    lows = [float(r["ci_low"]) for r in rows]
    highs = [float(r["ci_high"]) for r in rows]
    xerr = [[a - lo for a, lo in zip(acc, lows)], [hi - a for a, hi in zip(acc, highs)]]

    ax.barh(y, acc, color=colors, height=0.64, edgecolor="none", alpha=0.92)
    ax.errorbar(acc, y, xerr=xerr, fmt="none", ecolor="#544F48", elinewidth=0.55, capsize=1.4, capthick=0.55, zorder=3)
    for yi, a, hi in zip(y, acc, highs):
        ax.text(hi + 1.15, yi, f"{a:.1f}", va="center", ha="left", fontsize=4.35, color=MUTED, fontproperties=MONO)

    ax.set_yticks(y)
    ax.set_yticklabels([model_label(str(r["model"])) for r in rows], fontsize=4.9)
    ax.invert_yaxis()
    ax.set_xlim(0, 76)
    ax.set_xlabel("Endpoint pass rate (%)", fontsize=6.1, labelpad=2)
    ax.text(0.0, 1.125, "B  Endpoint grading", transform=ax.transAxes, fontsize=8.5, fontproperties=SERIF_BOLD, ha="left", va="bottom")
    ax.text(0.0, 1.070, "100 tasks x 3 attempts per model-harness pair", transform=ax.transAxes, fontsize=5.2, color=MUTED, fontproperties=SERIF, ha="left", va="bottom")
    ax.grid(axis="x", color=GRID, linewidth=0.45, alpha=0.75)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(AXIS)
    ax.tick_params(axis="x", labelsize=5.3, length=2, pad=1)
    ax.tick_params(axis="y", length=0, pad=1)


def pareto_frontier(rows: list[dict[str, float | str]]) -> list[dict[str, float | str]]:
    frontier: list[dict[str, float | str]] = []
    best = -1.0
    for row in sorted(rows, key=lambda r: (float(r["cost"]), -float(r["acc"]))):
        acc = float(row["acc"])
        if acc > best:
            frontier.append(row)
            best = acc
    return frontier


def draw_pareto_panel(ax: plt.Axes, rows: list[dict[str, float | str]]) -> None:
    frontier = pareto_frontier(rows)
    for harness, color in HARNESS_COLORS.items():
        subset = [r for r in rows if r["harness"] == harness]
        ax.scatter(
            [float(r["cost"]) for r in subset],
            [float(r["acc"]) for r in subset],
            s=19,
            color=color,
            edgecolor=WHITE,
            linewidth=0.45,
            alpha=0.95,
            zorder=5,
            label={"pi": "Pi", "claude-code": "Claude Code", "openai-codex": "Codex"}[harness],
        )

    ax.plot(
        [float(r["cost"]) for r in frontier],
        [float(r["acc"]) for r in frontier],
        color=ACCENT,
        linewidth=0.95,
        linestyle=(0, (1.2, 1.8)),
        alpha=0.9,
        zorder=2,
    )
    labels = {
        ("grok-4.3", "pi"): ((9, -10), "Grok 4.3", "left"),
        ("grok-4.20-0309-reasoning", "pi"): ((8, -7), "Grok 4.20", "left"),
        ("kimi-k2p6", "pi"): ((8, -12), "Kimi K2P6", "left"),
        ("claude-sonnet-4-6", "pi"): ((-10, -13), "Sonnet 4.6", "right"),
        ("gemini-3.1-pro-preview", "pi"): ((-14, 7), "Gemini 3.1", "right"),
        ("claude-opus-4-6", "pi"): ((-17, 16), "Opus 4.6", "right"),
        ("claude-opus-4-6", "claude-code"): ((18, -15), "Opus 4.6", "left"),
        ("gpt-5.4", "pi"): ((-4, 17), "GPT-5.4", "right"),
        ("gpt-5.4", "openai-codex"): ((18, -10), "GPT-5.4", "left"),
        ("claude-opus-4-7", "pi"): ((20, 5), "Opus 4.7", "left"),
        ("gpt-5.5", "openai-codex"): ((18, -3), "GPT-5.5", "left"),
        ("claude-opus-4-7", "claude-code"): ((19, -13), "Opus 4.7", "left"),
        ("gemini-3.5-flash", "pi"): ((18, -7), "Gemini 3.5", "left"),
        ("gpt-5.5", "pi"): ((14, 8), "GPT-5.5", "left"),
        ("claude-opus-4-8", "pi"): ((9, 11), "Opus 4.8", "left"),
        ("claude-opus-4-8", "claude-code"): ((-18, -9), "Opus 4.8", "right"),
    }
    for row in rows:
        key = (str(row["model"]), str(row["harness"]))
        if key not in labels:
            continue
        offset, txt, ha = labels[key]
        ax.annotate(
            txt,
            xy=(float(row["cost"]), float(row["acc"])),
            xytext=offset,
            textcoords="offset points",
            fontsize=3.75,
            color=TEXT,
            fontproperties=SERIF,
            ha=ha,
            va="center",
            arrowprops={
                "arrowstyle": "-",
                "color": MUTED,
                "lw": 0.35,
                "alpha": 0.72,
                "shrinkA": 1.0,
                "shrinkB": 2.0,
            },
            zorder=4,
        )

    ax.set_xlim(-0.04, 2.14)
    ax.set_ylim(13, 69)
    ax.set_xlabel("Mean cost per task ($)", fontsize=6.1, labelpad=2)
    ax.set_ylabel("Endpoint pass rate (%)", fontsize=6.1, labelpad=2)
    ax.set_title("C  Cost-performance frontier", loc="left", fontsize=8.5, fontproperties=SERIF_BOLD, pad=6)
    ax.grid(color=GRID, linewidth=0.45, alpha=0.75)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(AXIS)
    ax.spines["left"].set_color(AXIS)
    ax.tick_params(axis="both", labelsize=5.3, length=2, pad=1)
    ax.legend(loc="lower right", frameon=False, fontsize=5.1, handlelength=1.0, borderpad=0.1, labelspacing=0.25)


def fig_pipeline() -> None:
    rows = load_model_results()
    fig = plt.figure(figsize=(7.45, 6.55))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.24, 1.0], width_ratios=[1.12, 1.0], hspace=0.32, wspace=0.36)
    draw_scope_panel(fig.add_subplot(gs[0, :]))
    draw_passrate_panel(fig.add_subplot(gs[1, 0]), rows)
    draw_pareto_panel(fig.add_subplot(gs[1, 1]), rows)
    save(fig, "fig1_pipeline")


def fig_inventory() -> None:
    stages = [
        ("S1", "Disease / model\ncharacterization", 4, GRAY_DARK, False),
        ("S2", "Screening / hit\nconfirmation", 8, GOLD, False),
        ("S3", "Drug response /\npharmacogenomics", 10, GOLD, False),
        ("S4", "Human genetic\ntarget support", 0, GRAY, True),
        ("S5", "Causal target\nvalidation", 12, TEAL, False),
        ("S6", "MoA /\npharmacodynamics", 21, ACCENT, False),
        ("S7", "Compound-target\ncharacterization", 8, RED, False),
        ("S8", "Developability /\nsafety / PK", 20, RED, False),
        ("S9", "Translational\nefficacy", 17, VIOLET, False),
    ]
    assays = [
        ("Drug-response screens", 22, ACCENT),
        ("Image / histology / physiology", 17, VIOLET),
        ("Protein / phospho readouts", 16, VIOLET),
        ("Genetic perturbation", 12, TEAL),
        ("Target engagement / selectivity", 11, GOLD),
        ("Single-cell / molecular state", 8, TEAL),
        ("DMPK / safety profiling", 7, RED),
        ("In vivo / curated summaries", 7, GRAY_DARK),
    ]
    tasks = [
        ("MoA", 14, ACCENT),
        ("QC", 7, GOLD),
        ("Target dep.", 7, TEAL),
        ("Diff. response", 7, TEAL),
        ("Safety", 7, RED),
        ("Image", 6, VIOLET),
        ("Dim. reduction", 6, VIOLET),
        ("Phenotype", 6, VIOLET),
        ("Target engage.", 5, GOLD),
        ("Cheminfo", 5, GRAY_DARK),
        ("Exposure / PK", 4, ACCENT),
        ("Biomarker", 4, TEAL),
        ("Program call", 4, RED),
        ("Hit priority", 4, GOLD),
        ("Tail <4 each", 14, GRAY),
    ]
    max_assay = max(d[1] for d in assays)
    max_task = max(d[1] for d in tasks)
    fig, ax = plt.subplots(figsize=(7.35, 5.25))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    label(ax, 0.055, 0.958, "Benchmark anatomy", size=10.4, bold=True)
    label(
        ax,
        0.055,
        0.914,
        "Program stage locates the decision; assay type and task structure describe the data and work required.",
        size=6.9,
        color=MUTED,
    )

    # Panel A: where the decision sits in a program.
    rounded_box(ax, (0.045, 0.462), 0.910, 0.385, fc=WHITE, ec=LINE, lw=0.55, radius=0.014)
    label(ax, 0.063, 0.818, "A", size=7.0, color=ACCENT, bold=True, mono=True)
    label(ax, 0.086, 0.818, "Program stage", size=7.0, color=TEXT, bold=True)
    cell_w = 0.268
    cell_h = 0.075
    x0 = 0.068
    y0 = 0.682
    x_gap = 0.035
    y_gap = 0.027
    for i, (code, name, n, c, reserved) in enumerate(stages):
        row = i // 3
        col = i % 3
        x = x0 + col * (cell_w + x_gap)
        y = y0 - row * (cell_h + y_gap)
        fc = "#F0EEE9" if reserved else CREAM
        ec = LINE if reserved else c
        rounded_box(ax, (x, y), cell_w, cell_h, fc=fc, ec=ec, lw=0.7, radius=0.014)
        rounded_box(ax, (x + 0.012, y + 0.018), 0.038, 0.039, fc=c, ec="none", radius=0.008)
        label(ax, x + 0.031, y + 0.038, code, size=4.7, color=WHITE, bold=True, ha="center", mono=True)
        label(ax, x + 0.062, y + 0.047, name, size=5.1, bold=not reserved, color=MUTED if reserved else TEXT)
        count_text = "reserved*" if reserved else f"n={n}"
        label(ax, x + cell_w - 0.012, y + 0.020, count_text, size=4.6, mono=not reserved, bold=True, ha="right", color=MUTED if reserved else TEXT)

    # Panel B: evidence the agent must interpret.
    rounded_box(ax, (0.045, 0.105), 0.440, 0.305, fc=WHITE, ec=LINE, lw=0.55, radius=0.014)
    label(ax, 0.063, 0.381, "B", size=7.0, color=ACCENT, bold=True, mono=True)
    label(ax, 0.086, 0.381, "Assay type", size=7.0, color=TEXT, bold=True)
    for i, (txt, n, c) in enumerate(assays):
        y = 0.316 - i * 0.026
        label(ax, 0.065, y, txt, size=4.7, color=TEXT)
        ax.add_patch(Rectangle((0.280, y - 0.006), 0.105, 0.011, facecolor="#ECE7DF", edgecolor="none"))
        ax.add_patch(Rectangle((0.280, y - 0.006), 0.105 * n / max_assay, 0.011, facecolor=c, edgecolor="none"))
        label(ax, 0.407, y, f"{n}", size=4.7, mono=True, bold=True, ha="right")

    # Panel C: operation or judgment being graded.
    rounded_box(ax, (0.515, 0.105), 0.440, 0.305, fc=WHITE, ec=LINE, lw=0.55, radius=0.014)
    label(ax, 0.533, 0.381, "C", size=7.0, color=ACCENT, bold=True, mono=True)
    label(ax, 0.556, 0.381, "Task structure", size=7.0, color=TEXT, bold=True)
    for i, (txt, n, c) in enumerate(tasks):
        y = 0.319 - i * 0.0138
        label(ax, 0.535, y, txt, size=4.15, color=TEXT if i < len(tasks) - 1 else MUTED)
        ax.add_patch(Rectangle((0.700, y - 0.004), 0.112, 0.008, facecolor="#ECE7DF", edgecolor="none"))
        ax.add_patch(Rectangle((0.700, y - 0.004), 0.112 * n / max_task, 0.008, facecolor=c, edgecolor="none"))
        label(ax, 0.832, y, f"{n}", size=4.15, mono=True, bold=True, ha="right", color=TEXT if i < len(tasks) - 1 else MUTED)

    label(ax, 0.535, 0.080, "Task counts show categories with >=4 evaluations plus the smaller-category tail.", size=5.2, color=MUTED)
    label(
        ax,
        0.05,
        0.042,
        "* reserved for future benchmarking work",
        size=5.8,
        color=MUTED,
    )
    save(fig, "fig2_inventory")


def fig_failures() -> None:
    failures = [
        (
            "Literature prior over evidence",
            "Importing the known mechanism of a compound instead of reading the supplied assay footprint.",
            "decryptM, decryptE",
            ACCENT,
        ),
        (
            "Assay-context calibration failure",
            "Using the right workflow with the wrong tolerance, prompt context, species, or source convention.",
            "DM, DE, PK",
            TEAL,
        ),
        (
            "Multi-property integration gap",
            "Optimizing one attractive value while missing the property that changes the advancement decision.",
            "PK, ADMET, MPO",
            VIOLET,
        ),
        (
            "Rigid threshold shortcut",
            "Treating a rule-of-thumb cutoff as dispositive when margin or protocol context changes the call.",
            "PK / ADMET, TG",
            GOLD,
        ),
    ]
    fig, ax = plt.subplots(figsize=(7.2, 4.35))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    label(ax, 0.055, 0.955, "Failure modes should be read as program-relevant judgment gaps", size=10.8, bold=True)
    label(ax, 0.06, 0.895, "These categories should be replaced or quantified after trajectory review, but they define the expected diagnostic frame.", size=7.0, color=MUTED)

    for i, (head, body, ds, c) in enumerate(failures):
        x = 0.055 + (i % 2) * 0.465
        y = 0.56 if i < 2 else 0.215
        rounded_box(ax, (x, y), 0.405, 0.245, fc=CREAM, ec=LINE, radius=0.024)
        ax.add_patch(Rectangle((x, y + 0.220), 0.405, 0.025, facecolor=c, edgecolor="none"))
        label(ax, x + 0.022, y + 0.178, head, size=8.4, bold=True)
        label(ax, x + 0.022, y + 0.105, wrap(body, 50), size=6.65, color=TEXT)
        label(ax, x + 0.022, y + 0.034, ds, size=6.1, color=MUTED, mono=True, bold=True)
    save(fig, "fig3_failure_taxonomy")


def fig_cases() -> None:
    cases = [
        ("MoA", "Shortcut", "Use the drug-class label", "Data-supported", "Follow dose-resolved signalling", ACCENT),
        ("Target engagement", "Shortcut", "Keep strongest apparent protein", "Data-supported", "Remove contaminants; find cluster", VIOLET),
        ("Safety", "Shortcut", "Apply a generic blood-marker threshold", "Data-supported", "Integrate pathology, chemistry, survival", RED),
        ("PK / exposure", "Shortcut", "Rank by potency or total AUC", "Data-supported", "Compare unbound coverage", TEAL),
    ]
    fig, ax = plt.subplots(figsize=(7.25, 4.35))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    label(ax, 0.055, 0.955, "Representative task logic spans the preclinical pharmacology spine", size=10.8, bold=True)

    for i, (stage, bad_head, bad, good_head, good, c) in enumerate(cases):
        x = 0.055 + (i % 2) * 0.465
        y = 0.555 if i < 2 else 0.195
        rounded_box(ax, (x, y), 0.405, 0.275, fc=WHITE, ec=LINE, radius=0.024)
        label(ax, x + 0.022, y + 0.232, stage, size=8.3, bold=True)
        ax.plot([x + 0.022, x + 0.383], [y + 0.205, y + 0.205], color=LINE, lw=0.65)
        rounded_box(ax, (x + 0.022, y + 0.086), 0.162, 0.101, fc="#F5E9E4", ec="#E7C8B9", radius=0.014)
        rounded_box(ax, (x + 0.222, y + 0.086), 0.162, 0.101, fc="#E8F3F1", ec="#C5DDD9", radius=0.014)
        label(ax, x + 0.103, y + 0.168, bad_head, size=5.1, bold=True, ha="center", mono=True, color=ACCENT)
        label(ax, x + 0.303, y + 0.168, good_head, size=5.1, bold=True, ha="center", mono=True, color=TEAL_DARK if "TEAL_DARK" in globals() else TEAL)
        label(ax, x + 0.103, y + 0.122, wrap(bad, 19), size=5.1, ha="center")
        label(ax, x + 0.303, y + 0.122, wrap(good, 17), size=5.1, ha="center")
        ax.annotate("", xy=(x + 0.215, y + 0.148), xytext=(x + 0.190, y + 0.148),
                    arrowprops={"arrowstyle": "->", "lw": 0.7, "color": c})
        label(ax, x + 0.022, y + 0.050, "task asks for the defensible pharmacology decision", size=5.8, color=MUTED)
    save(fig, "fig4_cases")


def fig_program_decisions() -> None:
    """Three multi-evidence advancement decisions: one success, two failures."""
    TEAL_DARK = "#19736A"
    cards = [
        {
            "tag": "CORRECT",
            "tag_color": TEAL,
            "head": "Advance one compound, or none",
            "body": "Colorectal-cancer organoid program. Inputs: primary screen, "
            "mechanism image, tox counterscreen, DMPK exposure. Advance a compound "
            "only if the desired mechanism, an adequate safety margin, and covering "
            "exposure all hold.",
            "good": "Advance CMP-05, the one compound that satisfies all three "
            "criteria together.",
            "bad_head": "Mostly correct  (82% pass)",
            "bad": "The tempting shortcut, ranking by potency or by total exposure, "
            "advances the wrong compound.",
            "bad_fc": "#EEF3F1",
            "bad_ec": "#C9DDD9",
            "bad_color": TEAL_DARK,
        },
        {
            "tag": "WRONG SYNTHESIS",
            "tag_color": GOLD,
            "head": "Pick the next decision-gate models",
            "body": "NSCLC mTOR + WEE1 combination. The gate set must span models "
            "with confirmed multi-endpoint support, the strongest responder still "
            "lacking confirmation, and the strongest responder outside the primary "
            "genotype.",
            "good": "Build the gate on convergent multi-endpoint support "
            "(e.g. PDX239 for the unconfirmed slot).",
            "bad_head": "Common failure  (27% pass)",
            "bad": "Rank on a single synergy metric and nominate an artifact model "
            "(H2009), so the wrong models gate the program.",
            "bad_fc": "#F5E9E4",
            "bad_ec": "#E7C8B9",
            "bad_color": ACCENT,
        },
        {
            "tag": "FALSE-GO",
            "tag_color": RED,
            "head": "Advance only if safe and active",
            "body": "Blinded intestinal multiplex-IF package. A candidate may advance "
            "only with paired evidence of activity and healthy-tissue sparing.",
            "good": "No candidate advances; the paired activity-and-safety evidence "
            "fails for every candidate.",
            "bad_head": "Common failure  (36% pass)",
            "bad": "Advance on activity alone or a relative tumour-vs-healthy index, "
            "pushing an unsafe candidate forward.",
            "bad_fc": "#F5E9E4",
            "bad_ec": "#E7C8B9",
            "bad_color": ACCENT,
        },
    ]

    fig, ax = plt.subplots(figsize=(7.3, 5.15))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    label(ax, 0.04, 0.965, "Program decisions integrate several assay readouts into one go/no-go", size=10.2, bold=True)
    label(
        ax,
        0.04,
        0.922,
        "Across 7 such advancement evaluations (230 runs) models pass only 35%; the same call can fail by advancing too much or too little.",
        size=6.7,
        color=MUTED,
    )

    top0 = 0.862
    row_h = 0.262
    gap = 0.022
    for i, c in enumerate(cards):
        top = top0 - i * (row_h + gap)
        bot = top - row_h
        rounded_box(ax, (0.04, bot), 0.92, row_h, fc=WHITE, ec=LINE, lw=0.7, radius=0.012)
        # outcome tag strip
        rounded_box(ax, (0.04, bot), 0.026, row_h, fc=c["tag_color"], ec="none", radius=0.012)
        ax.text(0.053, bot + row_h / 2, c["tag"], fontsize=5.0, color=WHITE,
                fontproperties=MONO_BOLD, ha="center", va="center", rotation=90)
        # column A: context
        label(ax, 0.085, top - 0.040, c["head"], size=7.2, bold=True)
        label(ax, 0.085, top - 0.135, wrap(c["body"], 52), size=5.5, color=TEXT)
        # column B: supported call
        gx, gw = 0.470, 0.235
        rounded_box(ax, (gx, bot + 0.030), gw, row_h - 0.060, fc="#EEF3F1", ec="#C9DDD9", lw=0.6, radius=0.016)
        label(ax, gx + 0.014, top - 0.052, "DATA-SUPPORTED CALL", size=4.9, bold=True, mono=True, color=TEAL_DARK)
        label(ax, gx + 0.014, top - 0.115, wrap(c["good"], 30), size=5.5, color=TEXT)
        # column C: common failure + consequence
        bx, bw = 0.715, 0.235
        rounded_box(ax, (bx, bot + 0.030), bw, row_h - 0.060, fc=c["bad_fc"], ec=c["bad_ec"], lw=0.6, radius=0.016)
        label(ax, bx + 0.014, top - 0.052, c["bad_head"].upper(), size=4.9, bold=True, mono=True, color=c["bad_color"])
        label(ax, bx + 0.014, top - 0.115, wrap(c["bad"], 30), size=5.5, color=TEXT)

    save(fig, "fig_program_decisions")


if __name__ == "__main__":
    TEAL_DARK = "#19736A"
    fig_pipeline()
    fig_inventory()
    fig_failures()
    fig_cases()
    fig_program_decisions()
