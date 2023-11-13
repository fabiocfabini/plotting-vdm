from __future__ import annotations
from typing import List
from dataclasses import dataclass, field
from pathlib import Path


def get_default_colors() -> List[str]:
    return ["k", "r", "g", "b", "m", "c", "y"]


@dataclass
class PlotterCongig:
    output_dir: Path = Path("plots")
    file_suffix: str = ""
    file_ext: str = "png"
    colors: List[str] = field(default_factory=get_default_colors)


@dataclass
class EvoPlotterConfig(PlotterCongig):
    xticks: List[str] = field(default_factory=list)
