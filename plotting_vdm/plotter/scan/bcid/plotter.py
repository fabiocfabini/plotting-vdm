from itertools import product
from dataclasses import dataclass
from typing import Optional

import matplotlib.pyplot as plt

from plotting_vdm.plotter.scan.base import Plotter
from plotting_vdm.plotter.config import PlotterCongig
from plotting_vdm.scan_results import ScanResults
from .strategy import BCIDPlotStrategy


@dataclass
class BCIDPlotter(Plotter):
    config: PlotterCongig
    plot_strategy: Optional[BCIDPlotStrategy] = None

    def set_strategy(self, plot_strategy: BCIDPlotStrategy):
        if not isinstance(plot_strategy, BCIDPlotStrategy):
            raise TypeError(f"Expected BCIDPlotStrategy, got {type(plot_strategy)}")

        self.plot_strategy = plot_strategy

    def plot(self, result: ScanResults):
        if self.plot_strategy is None:
            raise ValueError("Plot strategy not set")

        for fit, correction in product(result.fits, result.corrections):
            if self.plot_strategy.plot_per_detector:
                self._plot_per_detector(result, fit, correction)
            else:
                self._not_plot_per_detector(result, fit, correction)

    def _not_plot_per_detector(self, result: ScanResults, fit: str, correction: str):
        for i, detector in enumerate(result.detectors):
            plt.cla()

            data = result.results[fit].query(
                f"detector == '{detector}' and correction == '{correction}'")
            self.plot_strategy.do_plot(data, label=detector, color=self.config.colors[i])

            self._post_plot(result, fit, correction)

    def _plot_per_detector(self, result: ScanResults, fit: str, correction: str):
        plt.cla()
        for i, detector in enumerate(result.detectors):
            data = result.results[fit].query(
                f"detector == '{detector}' and correction == '{correction}'")
            self.plot_strategy.do_plot(data, label=detector, color=self.config.colors[i])

        self._post_plot(result, fit, correction)

    def _post_plot(self, result: ScanResults, fit: str, correction: str):
        self.plot_strategy.style_plot(
            scan_name=result.name, fit=fit, correction=correction
        )

        self.plot_strategy.save_plot(
            self.config.output_dir/result.id_str,
            f"{fit}_{correction}",
            suffix=self.config.file_suffix,
            file_ext=self.config.file_ext
        )
