#!/usr/bin/env python3
"""Normalize pre-rendered result figures to the paper palette.

Some result panels are checked in only as PDFs.  Convert them through SVG so we
can remap data colors without changing text, axes, or layout.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "paper" / "figures"

FIGURES = [
    "fig3_failure_taxonomy_granular",
    "fig_by_stage",
    "fig_program_model_compare",
    "fig_harness_impact",
]

BASE_COLOR_MAP = {
    # Data colors from older result figures -> Figure 1 / paper palette.
    "rgb(31.37207%, 43.920898%, 56.469727%)": "#5f6872",
    "rgb(75.292969%, 43.920898%, 25.097656%)": "#a95f3d",
    "rgb(18.823242%, 62.744141%, 56.469727%)": "#2a9d8f",
    "rgb(12.156677%, 43.528748%, 38.822937%)": "#1f6f63",
    "rgb(43.920898%, 37.646484%, 75.292969%)": "#7267c8",
    "rgb(69.018555%, 56.469727%, 25.097656%)": "#b89142",
    "rgb(61.959839%, 78.822327%, 74.116516%)": "#a9cec4",
    "rgb(47.842407%, 47.842407%, 47.842407%)": "#8d867e",
    # Light support colors used for fills, uncertainty ribbons, and low-value bins.
    "rgb(80.39093%, 74.900818%, 61.959839%)": "#ddd7cb",
    "rgb(85.096741%, 61.959839%, 47.058105%)": "#c97745",
    "rgb(93.72406%, 90.586853%, 84.70459%)": "#f8f3ed",
    "rgb(87.496948%, 88.28125%, 82.629395%)": "#d9dee5",
    "rgb(90.795898%, 79.606628%, 57.98645%)": "#d9c277",
    "rgb(91.485596%, 82.189941%, 64.273071%)": "#e2d09e",
    "rgb(92.076111%, 84.405518%, 69.66095%)": "#e8dcc1",
    "rgb(92.863464%, 87.358093%, 76.846313%)": "#f0eee9",
    "rgb(93.553162%, 89.941406%, 83.132935%)": "#f8f3ed",
}

FIG3_STYLE_MAP = {
    # Figures 4 and 5 use many categorical colors.  Keep them closer to the
    # Figure 3 palette by replacing extra pastel hues with the same neutral,
    # teal, violet, and terracotta family used in the topline result.
    "#1f6f63": "#8d867e",
    "#a9cec4": "#b8b2aa",
    "#b89142": "#c97745",
    "#d9c277": "#c97745",
    "#e2d09e": "#b8b2aa",
    "#e8dcc1": "#eee8dc",
    "#f0eee9": "#f8f5ee",
    "#f8f3ed": "#f8f5ee",
    "rgb(12.156677%, 43.528748%, 38.822937%)": "#8d867e",
    "rgb(66.273499%, 80.783081%, 76.861572%)": "#b8b2aa",
    "rgb(72.155762%, 56.861877%, 25.881958%)": "#c97745",
    "rgb(85.096741%, 76.077271%, 46.665955%)": "#c97745",
    "rgb(88.626099%, 81.567383%, 61.959839%)": "#b8b2aa",
    "rgb(90.979004%, 86.273193%, 75.68512%)": "#eee8dc",
    "rgb(94.116211%, 93.331909%, 91.371155%)": "#f8f5ee",
    "rgb(97.253418%, 95.292664%, 92.939758%)": "#f8f5ee",
}

FIGURE_SPECIFIC_MAPS = {
    "fig3_failure_taxonomy_granular": FIG3_STYLE_MAP,
    "fig_by_stage": FIG3_STYLE_MAP,
}


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, cwd=ROOT)


def main() -> None:
    if shutil.which("pdftocairo") is None:
        raise SystemExit("pdftocairo is required to recolor pre-rendered figures")
    if shutil.which("rsvg-convert") is None:
        raise SystemExit("rsvg-convert is required to regenerate recolored PDFs")

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        for stem in FIGURES:
            pdf = FIG_DIR / f"{stem}.pdf"
            if not pdf.exists():
                raise SystemExit(f"Missing figure: {pdf}")

            svg = tmp / f"{stem}.svg"
            recolored = tmp / f"{stem}_recolored.svg"
            run(["pdftocairo", "-svg", str(pdf), str(svg)])

            text = svg.read_text()
            color_map = dict(BASE_COLOR_MAP)
            color_map.update(FIGURE_SPECIFIC_MAPS.get(stem, {}))
            for old, new in color_map.items():
                text = text.replace(old, new)
            recolored.write_text(text)

            run(["rsvg-convert", "-f", "pdf", "-o", str(pdf), str(recolored)])

            png = FIG_DIR / f"{stem}.png"
            if png.exists():
                run(
                    [
                        "rsvg-convert",
                        "-f",
                        "png",
                        "-d",
                        "220",
                        "-p",
                        "220",
                        "-o",
                        str(png),
                        str(recolored),
                    ]
                )


if __name__ == "__main__":
    main()
