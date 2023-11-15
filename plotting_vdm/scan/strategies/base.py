from typing import Dict, Any
from pathlib import Path

from plotting_vdm.scan_results import ScanResults



class PlotStrategy:
    def __init__(self, **kwargs):
        self.context: Dict[str, Any] = {}

        self.xlabel = kwargs.get("xlabel", "BCID")
        self.legend_loc = kwargs.get("legend_loc", "best")
        self.output_dir: Path = kwargs.get("output_dir", Path("."))
        if not isinstance(self.output_dir, Path):
            self.output_dir = Path(self.output_dir)
        self.output_dir = self.output_dir/"plots"
        self.fmt = kwargs.get("fmt", "o")
        self.legend_fontsize = kwargs.get("legend_fontsize", 12)
        self.colors = kwargs.get("colors", ["k", "r", "b", "g", "m", "c", "y"])
        self.markersize = kwargs.get("markersize", 5)

    def on_correction_loop_entry(self, results: ScanResults, fit: str, correction: str) -> bool:
        """
        on_correction_loop_entry
        """
        return False

    def on_detector_loop(self, i, results: ScanResults, fit: str, correction: str, detector: str):
        """
        on_detector_loop
        """

    def on_correction_loop_exit(self, results: ScanResults, fit: str, correction: str):
        """
        on_correction_loop_exit
        """