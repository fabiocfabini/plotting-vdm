from typing import Dict, Any, Sequence
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from plotting_vdm.scan_results import ScanResults
from plotting_vdm.utils.title_builder import TitleBuilder


class PlotStrategy:
    def __init__(self, quantity: str, error: str, quantity_latex: str = "", **kwargs):
        self.context: Dict[str, Any] = {}
        self.quantity = quantity
        self.error = error
        self.quantity_latex = quantity_latex if quantity_latex else quantity

        self.xlabel = kwargs.get("xlabel", "Scan Name")
        self.legend_loc = kwargs.get("legend_loc", "best")
        self.output_dir: Path = kwargs.get("output_dir", Path("."))
        if not isinstance(self.output_dir, Path):
            self.output_dir = Path(self.output_dir)
        self.output_dir = self.output_dir/"plots"/"evo"
        self.fmt = kwargs.get("fmt", "o")
        self.legend_fontsize = kwargs.get("legend_fontsize", 12)
        self.colors = kwargs.get("colors", ["k", "r", "b", "g", "m", "c", "y"])
        self.markersize = kwargs.get("markersize", 5)
        self.ticks_fontsize = kwargs.get("ticks_fontsize", 8)
        self.ticks_rotation = kwargs.get("ticks_rotation", 0)

    def on_correction_loop_entry(self, results: Sequence[ScanResults], fit: str, correction: str):
        """
        on_correction_loop_entry
        """
        plt.clf()

    def on_detector_loop(self, i, results: Sequence[ScanResults], fit: str, correction: str, detector: str):
        """
        on_detector_loop
        """
        x_values = np.arange(1, len(results)+1)
        y_values = np.empty(len(results))
        y_errors = np.empty(len(results))

        for j, result in enumerate(results):
            data = result.filter_results_by(fit, correction, detector, quality="good")

            y_values[j] = data[self.quantity].mean()
            y_errors[j] = data[self.quantity].std()

        plt.errorbar(
            x_values,
            y_values,
            yerr=y_errors,
            fmt=self.fmt,
            color=self.colors[i],
            label=detector,
            markersize=self.markersize
        )

    def on_correction_loop_exit(self, results: Sequence[ScanResults], fit: str, correction: str):
        """
        on_correction_loop_exit
        """
        title = TitleBuilder() \
                .set_fit(fit) \
                .set_info(self.quantity_latex) \
                .set_correction(correction).build()
        ticks = [result.name for result in results]

        plt.xlim(0, len(results)+1)
        plt.grid()
        plt.title(title)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.quantity_latex)
        plt.legend(loc=self.legend_loc, fontsize=self.legend_fontsize)
        plt.xticks(range(1, len(results)+1), ticks, rotation=self.ticks_rotation, fontsize=self.ticks_fontsize)

        path = self.output_dir/self.quantity/fit
        path.mkdir(parents=True, exist_ok=True)

        file = f"{correction}.png"
        plt.savefig(path/file)


class SeparatePlotStrategy(PlotStrategy):
    def __init__(self, quantity: str, error: str, quantity_latex: str = "", **kwargs):
        self.context: Dict[str, Any] = {}
        self.quantity = quantity
        self.error = error
        self.quantity_latex = quantity_latex if quantity_latex else quantity

        self.xlabel = kwargs.get("xlabel", "Scan Name")
        self.legend_loc = kwargs.get("legend_loc", "best")
        self.output_dir: Path = kwargs.get("output_dir", Path("."))
        if not isinstance(self.output_dir, Path):
            self.output_dir = Path(self.output_dir)
        self.output_dir = self.output_dir/"plots"/"evo"
        self.fmt = kwargs.get("fmt", "o")
        self.legend_fontsize = kwargs.get("legend_fontsize", 12)
        self.colors = kwargs.get("colors", ["k", "r", "b", "g", "m", "c", "y"])
        self.markersize = kwargs.get("markersize", 5)
        self.ticks_fontsize = kwargs.get("ticks_fontsize", 8)
        self.ticks_rotation = kwargs.get("ticks_rotation", 0)

    def on_correction_loop_entry(self, results: Sequence[ScanResults], fit: str, correction: str):
        """
        on_correction_loop_entry
        """

    def on_detector_loop(self, i, results: Sequence[ScanResults], fit: str, correction: str, detector: str):
        """
        on_detector_loop
        """
        plt.clf()
        x_values = np.arange(1, len(results)+1)
        y_values = np.empty(len(results))
        y_errors = np.empty(len(results))

        for j, result in enumerate(results):
            data = result.filter_results_by(fit, correction, detector, quality="good")

            y_values[j] = data[self.quantity].mean()
            y_errors[j] = data[self.quantity].std()

        plt.errorbar(
            x_values,
            y_values,
            yerr=y_errors,
            fmt=self.fmt,
            color=self.colors[i],
            markersize=self.markersize
        )

        title = TitleBuilder() \
                .set_fit(fit) \
                .set_info(self.quantity_latex) \
                .set_detector(detector) \
                .set_correction(correction).build()
        ticks = [result.name for result in results]

        plt.xlim(0, len(results)+1)
        plt.grid()
        plt.title(title)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.quantity_latex)
        plt.xticks(range(1, len(results)+1), ticks, rotation=self.ticks_rotation, fontsize=self.ticks_fontsize)

        path = self.output_dir/self.quantity/"seperate"/fit/detector
        path.mkdir(parents=True, exist_ok=True)

        file = f"{correction}.png"
        plt.savefig(path/file)

    def on_correction_loop_exit(self, results: Sequence[ScanResults], fit: str, correction: str):
        """
        on_correction_loop_exit
        """
