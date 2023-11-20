from typing import Dict, Any
from pathlib import Path

from plotting_vdm.scan_results import ScanResults
from plotting_vdm._typing import OneOrMany


class PlotStrategy:
    """Base class for plot strategies.
    A class that inherits from this class can be used to define a custom plotting strategy.
    A plotting strategy consists of three methods:
        - `on_correction_loop_entry`: This method is called upon entering the correction loop.
        - `on_detector_loop`: This method is called upon entering the detector loop.
        - `on_correction_loop_exit`: This method is called before exiting the correction loop.
    To better understand the positioning of these methods, see the VdMPlotter class in `plotting_vdm/plotter.py`.

    Parameters
    ----------
    context : Dict[str, Any], default: {}
        Context dictionary, used to pass information between the different methods.
    xlabel : str, default: ""
        Label for the x-axis.
    legend_loc : str, default: "best"
        Location of the legend.
    output_dir : Path or str, default: "."
        Output directory for the plots. "plots" will be appended to this path.
    fmt : str, default: "o"
        Format of the markers.
    legend_fontsize : int, default: 12
        Fontsize of the legend.
    colors : list, default: ["k", "r", "b", "g", "m", "c", "y"]
        List of colors to use for the different detectors.
    markersize : int, default: 5
        Size of the markers.
    """

    def __init__(self, **kwargs):
        self.context: Dict[str, Any] = {}
        self.xlabel: str = kwargs.get("xlabel", "")
        self.legend_loc: str = kwargs.get("legend_loc", "best")
        self.output_dir: Path = kwargs.get("output_dir", Path("."))
        if not isinstance(self.output_dir, Path):
            self.output_dir = Path(self.output_dir)
        self.output_dir = self.output_dir/"plots"
        self.fmt: str = kwargs.get("fmt", "o")
        self.legend_fontsize: int = kwargs.get("legend_fontsize", 12)
        self.colors: list = kwargs.get("colors", ["k", "r", "b", "g", "m", "c", "y"])
        self.markersize: int = kwargs.get("markersize", 5)

    def on_correction_loop_entry(self, results: OneOrMany[ScanResults], fit: str, correction: str) -> bool:
        """
        TODO: Add docstring
        """
        return False

    def on_detector_loop(self, i, results: OneOrMany[ScanResults], fit: str, correction: str, detector: str):
        """
        TODO: Add docstring
        """

    def on_correction_loop_exit(self, results: OneOrMany[ScanResults], fit: str, correction: str):
        """
        TODO: Add docstring
        """
