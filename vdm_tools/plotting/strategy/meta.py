from dataclasses import dataclass, field

def _get_default_colors():
    return ["k", "r", "b", "g", "m", "c", "y"]

@dataclass
class StrategyMeta:
    fmt: str = "o"
    markersize: float = 5
    elinewidth: float = 1.0
    colors: list =  field(default_factory=_get_default_colors)
    legend_loc: str = "best"
    legend_fontsize: int = 12
