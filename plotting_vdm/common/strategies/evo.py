from typing import Tuple
from collections.abc import Sequence

import numpy as np
import matplotlib.pyplot as plt

from plotting_vdm.scan_results import ScanResults
from plotting_vdm._typing import OneOrMany
from plotting_vdm.utils.title_builder import TitleBuilder
from .base import PlotStrategy


def compute_plot_range(results: OneOrMany[ScanResults]) -> Tuple[int, int]:
    if isinstance(results, Sequence):
        max_fill = max([result.fill_number for result in results])
        min_fill = min([result.fill_number for result in results])
        return min_fill, max_fill

    return results.fill_number, results.fill_number


class EvoPlotStrategy(PlotStrategy):
    def __init__(self, quantity: str, error: str, quantity_latex: str = "", **kwargs):
        super().__init__(**kwargs)
        self.quantity = quantity
        self.error = error
        self.quantity_latex = quantity_latex if quantity_latex else quantity

        self.output_dir = self.output_dir/"evo"
        self.xlabel = kwargs.get("xlabel", "Scan Name")
        self.ticks_fontsize = kwargs.get("ticks_fontsize", 8)
        self.ticks_rotation = kwargs.get("ticks_rotation", 0)

    def on_correction_loop_entry(self, results: OneOrMany[ScanResults], fit: str, correction: str):
        """
        on_correction_loop_entry
        """
        plt.clf()

    def on_detector_loop(self, i, results: OneOrMany[ScanResults], fit: str, correction: str, detector: str):
        """
        on_detector_loop
        """
        assert isinstance(results, list)
        x_values = np.arange(1, len(results)+1)
        y_values = np.empty(len(results))
        y_errors = np.empty(len(results))

        for j, result in enumerate(results):
            data = result.filter_results_by(fit, correction, detector, quality=self.data_quality)

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

    def on_correction_loop_exit(self, results: OneOrMany[ScanResults], fit: str, correction: str):
        """
        on_correction_loop_exit
        """
        assert isinstance(results, list)
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

        min_fill, max_fill = compute_plot_range(results)
        path = self.output_dir/f"{min_fill}-{max_fill}"/self.quantity/fit
        path.mkdir(parents=True, exist_ok=True)

        file = f"{correction}.png"
        plt.savefig(path/file)


class EvoSeparatePlotStrategy(PlotStrategy):
    def __init__(self, quantity: str, error: str, quantity_latex: str = "", **kwargs):
        super().__init__(**kwargs)
        self.quantity = quantity
        self.error = error
        self.quantity_latex = quantity_latex if quantity_latex else quantity

        self.output_dir = self.output_dir/"evo"
        self.xlabel = kwargs.get("xlabel", "Scan Name")
        self.ticks_fontsize = kwargs.get("ticks_fontsize", 8)
        self.ticks_rotation = kwargs.get("ticks_rotation", 0)
        self.color = kwargs.get("color", "blue")

    def on_detector_loop(self, i, results: OneOrMany[ScanResults], fit: str, correction: str, detector: str):
        """
        on_detector_loop
        """
        assert isinstance(results, list)
        plt.clf()
        x_values = np.arange(1, len(results)+1)
        y_values = np.empty(len(results))
        y_errors = np.empty(len(results))

        for j, result in enumerate(results):
            data = result.filter_results_by(fit, correction, detector, quality=self.data_quality)

            y_values[j] = np.average(data[self.quantity], weights=1/data[self.error]**2)
            y_errors[j] = np.sqrt(np.average((data[self.quantity]-y_values[j])**2, weights=1/data[self.error]**2))

        plt.errorbar(
            x_values,
            y_values,
            yerr=y_errors,
            fmt=self.fmt,
            color=self.color,
            markersize=self.markersize,
            elinewidth=0.5,
        )

        plt.xlim(0, len(results)+1)
        w_avg = np.average(y_values, weights=1/y_errors**2)
        w_rms = np.sqrt(np.average((y_values-w_avg)**2, weights=1/y_errors**2))
        plt.axhline(w_avg, color="red", label=f"{self.quantity_latex} {w_avg:.2f} RMS {w_rms:.2f}. ({w_rms/w_avg*100:.2f} %)")
        plt.axhline(w_avg-w_rms, color="orange", linestyle="--", alpha=0.9)
        plt.axhline(w_avg+w_rms, color="orange", linestyle="--", alpha=0.9)
        plt.fill_between(plt.xlim(), w_avg-w_rms, w_avg+w_rms, color="orange", alpha=0.3)

        title = TitleBuilder() \
                .set_fit(fit) \
                .set_info(self.quantity_latex) \
                .set_detector(detector) \
                .set_correction(correction).build()
        ticks = [result.name for result in results]

        plt.grid()
        plt.title(title)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.quantity_latex)
        plt.xticks(range(1, len(results)+1), ticks, rotation=self.ticks_rotation, fontsize=self.ticks_fontsize)
        plt.ticklabel_format(useOffset=False, axis="y")
        plt.legend(loc=self.legend_loc, fontsize=self.legend_fontsize)

        min_fill, max_fill = compute_plot_range(results)
        path = self.output_dir/f"{min_fill}-{max_fill}"/self.quantity/"seperate"/fit/detector
        path.mkdir(parents=True, exist_ok=True)

        file = f"{correction}.png"
        plt.savefig(path/file)
