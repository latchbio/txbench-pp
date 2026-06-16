#!/usr/bin/env python3
"""Generate TxBench-PP paper template figures."""
from __future__ import annotations

import os
import textwrap
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-cache")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import FancyBboxPatch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "paper" / "figures"

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


def fig_pipeline() -> None:
    columns = [
        "Discovery",
        "Development",
        "Translation",
    ]
    rows = [
        (
            "Small\nmolecule",
            [
                ("MoA / pathway\nTarget engagement", ACCENT),
                ("ADMET / DMPK\nPK source choice", TEAL),
                ("Safety / tox\nExposure margin", RED),
            ],
            "TxBench-PP",
        ),
        (
            "Biologic",
            [("binding kinetics\nimmunogenicity", GRAY), ("developability\nPK/PD", GRAY), ("NHP safety\nhuman dose", GRAY)],
            "future",
        ),
        (
            "Oligo",
            [("guide ranking\nknockdown", GRAY), ("delivery\nclearance", GRAY), ("chronic safety\ntranslation", GRAY)],
            "future",
        ),
    ]
    detail_boxes = [
        ("DM", "decryptM", VIOLET),
        ("DE", "decryptE", TEAL),
        ("KB", "Kinobeads", GOLD),
        ("TG", "TG-GATEs", RED),
        ("PK", "PK/ADMET", ACCENT),
    ]

    fig, ax = plt.subplots(figsize=(7.45, 4.85))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    label(ax, 0.055, 0.955, "TxBench-PP is a focused small-molecule slice of TherapeuticsBench", size=10.3, bold=True)
    label(
        ax,
        0.055,
        0.905,
        "The broader roadmap is organized by stage and modality; the current benchmark tests recurring cluster decisions.",
        size=7.1,
        color=MUTED,
    )

    left = 0.220
    cell_w = 0.215
    cell_h = 0.106
    col_gap = 0.026
    row_gap = 0.043
    row0_y = 0.595
    for j, head in enumerate(columns):
        x = left + j * (cell_w + col_gap)
        rounded_box(ax, (x, 0.748), cell_w, 0.052, fc=CREAM, ec=LINE, lw=0.45, radius=0.012)
        label(ax, x + cell_w / 2, 0.774, head, size=7.5, bold=True, ha="center")

    for i, (row_name, cells, tag) in enumerate(rows):
        y = row0_y - i * (cell_h + row_gap)
        label(ax, 0.060, y + cell_h * 0.58, row_name, size=7.0, bold=True, ha="left")
        label(ax, 0.060, y + 0.020, tag, size=5.5, color=ACCENT if tag == "TxBench-PP" else MUTED, bold=True, mono=True)
        for j, (txt, c) in enumerate(cells):
            x = left + j * (cell_w + col_gap)
            fc = c if tag == "TxBench-PP" else "#F0EEE9"
            ec = "none" if tag == "TxBench-PP" else LINE
            rounded_box(ax, (x, y), cell_w, cell_h, fc=fc, ec=ec, lw=0.55, radius=0.016)
            label(
                ax,
                x + cell_w / 2,
                y + cell_h / 2,
                txt,
                size=6.3,
                color=WHITE if tag == "TxBench-PP" else MUTED,
                bold=tag == "TxBench-PP",
                ha="center",
            )

    rounded_box(ax, (0.055, 0.154), 0.418, 0.084, fc=CREAM, ec=LINE, radius=0.018)
    rounded_box(ax, (0.527, 0.154), 0.418, 0.084, fc=WHITE, ec=LINE, radius=0.018)
    label(ax, 0.078, 0.211, "Cluster benchmark now", size=6.9, bold=True)
    label(ax, 0.078, 0.178, "Repeated decisions across assays and compounds", size=5.9, color=MUTED)
    label(ax, 0.550, 0.211, "Program stories later", size=6.9, bold=True)
    label(ax, 0.550, 0.178, "Long-horizon reasoning across program stages", size=5.9, color=MUTED)

    label(ax, 0.055, 0.095, "Current evidence sources", size=6.5, color=MUTED, bold=True, mono=True)
    for i, (code, name, c) in enumerate(detail_boxes):
        x = 0.300 + i * 0.128
        rounded_box(ax, (x, 0.065), 0.120, 0.052, fc=CREAM, ec=LINE, radius=0.011)
        rounded_box(ax, (x + 0.009, 0.078), 0.029, 0.026, fc=c, ec="none", radius=0.006)
        label(ax, x + 0.0235, 0.091, code, size=4.8, color=WHITE, bold=True, ha="center", mono=True)
        label(ax, x + 0.044, 0.091, name, size=4.45, bold=True)

    save(fig, "fig1_pipeline")


def fig_inventory() -> None:
    stages = [
        ("S1", "Disease / model\ncharacterization", 0, "Deferred", "out of v1 scope", GRAY_DARK),
        ("S2", "Primary screening\n& hit confirmation", 7, "Diversify", "PRISM-heavy", GOLD),
        ("S3", "Drug response /\npharmacogenomics", 11, "Diversify", "mostly PRISM", GOLD),
        ("S4", "Human genetic\ntarget support", 0, "Deferred", "GenomicsBench", GRAY_DARK),
        ("S5", "Causal target\nvalidation", 12, "Ready", "v1 coverage", TEAL),
        ("S6", "MoA /\npharmacodynamics", 17, "Ready", "strongest coverage", TEAL),
        ("S7", "Compound-target\ncharacterization", 1, "Build", "largest gap", RED),
        ("S8", "Developability\n& safety", 16, "Diversify", "cardiotox-heavy", ACCENT),
        ("S9", "Translational\nefficacy", 6, "Diversify", "one NSCLC source", ACCENT),
    ]
    max_eval = max(d[2] for d in stages)
    fig, ax = plt.subplots(figsize=(7.35, 4.65))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    label(ax, 0.055, 0.955, "Evaluation inventory follows the nine-stage Assays Roadmap", size=10.4, bold=True)
    label(ax, 0.055, 0.905, "Coverage is broad by stage count, but several covered stages remain single-source dominated.", size=7.0, color=MUTED)

    summary = [("70", "evals"), ("7/9", "stages covered"), ("S7", "build gap")]
    widths = [0.135, 0.165, 0.150]
    starts = [0.055, 0.210, 0.395]
    for i, (big, small) in enumerate(summary):
        x = starts[i]
        rounded_box(ax, (x, 0.807), widths[i], 0.065, fc=CREAM, ec=LINE, radius=0.012)
        label(ax, x + 0.022, 0.842, big, size=9.0, bold=True, mono=True, color=ACCENT if i == 2 else TEXT)
        label(ax, x + 0.068, 0.842, small, size=5.9, color=MUTED, bold=True if i == 2 else False)

    headers = ["Stage", "Evals", "Status", "Roadmap interpretation"]
    xs = [0.055, 0.455, 0.598, 0.735]
    for x, h in zip(xs, headers):
        label(ax, x, 0.750, h, size=6.2, color=MUTED, bold=True, mono=True)
    ax.plot([0.05, 0.955], [0.725, 0.725], color=LINE, lw=0.9)

    row_h = 0.071
    y0 = 0.678
    for i, (code, name, n, status, note, c) in enumerate(stages):
        y = y0 - i * row_h
        rounded_box(ax, (0.045, y - 0.030), 0.91, 0.058, fc=WHITE if i % 2 else CREAM, ec=LINE, lw=0.30, radius=0.010)
        rounded_box(ax, (0.058, y - 0.020), 0.038, 0.040, fc=c, ec="none", radius=0.008)
        label(ax, 0.077, y, code, size=6.2, color=WHITE, bold=True, ha="center", mono=True)
        label(ax, 0.108, y, name, size=5.65, bold=True)
        ax.add_patch(Rectangle((0.455, y - 0.010), 0.098, 0.020, facecolor="#ECE7DF", edgecolor="none"))
        if n > 0:
            ax.add_patch(Rectangle((0.455, y - 0.010), 0.098 * n / max_eval, 0.020, facecolor=c, edgecolor="none"))
        label(ax, 0.568, y, f"{n}", size=5.6, mono=True, bold=True, ha="right")
        rounded_box(ax, (0.598, y - 0.018), 0.100, 0.036, fc=c, ec="none", radius=0.009)
        label(ax, 0.648, y, status, size=5.0, color=WHITE, bold=True, ha="center", mono=True)
        label(ax, 0.735, y, note, size=5.55, color=TEXT if status != "Deferred" else MUTED)

    label(
        ax,
        0.05,
        0.030,
        "Counts and statuses are from the Assays Roadmap coverage mapping. S1 and S4 are intentionally deferred for this release.",
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
