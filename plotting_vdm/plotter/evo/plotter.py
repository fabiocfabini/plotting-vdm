from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence, Optional
from itertools import product

import matplotlib.pyplot as plt

from plotting_vdm.scan_results import ScanResults
from plotting_vdm.plotter.config import EvoPlotterConfig
from .strategy import EvoPlotStrategy


@dataclass
class EvoPlotter:
    config: EvoPlotterConfig
    plot_strategy: Optional[EvoPlotStrategy] = None

    def __call__(self, result: Sequence[ScanResults]):
        plt.figure()
        self.plot(result)
        plt.close()

    def plot_many(self, results: Sequence[Sequence[ScanResults]]):
        for result in results:
            self(result)

    def plot(self, results: Sequence[ScanResults]):
        if self.plot_strategy is None:
            raise ValueError("Plot strategy not set")

        fits = results[0].fits
        corrections = results[0].corrections

        for fit, correction in product(fits, corrections):
            if self.plot_strategy.plot_per_detector:
                self._plot_per_detector(results, fit, correction)
            else:
                self._not_plot_per_detector(results, fit, correction)

    def _plot_per_detector(self, results: Sequence[ScanResults], fit: str, correction: str):
        for i, detector in enumerate(results[0].detectors):
            plt.cla()
            
            datas = [
                result.results[fit]\
                    .query(f"detector == '{detector}' and correction == '{correction}'")
                for result in results
            ]

            self.plot_strategy.do_plot(datas, label=detector, color=self.config.colors[i])
            self._post_plot(fit, correction)

    def _not_plot_per_detector(self, results: Sequence[ScanResults], fit: str, correction: str):
        plt.cla()

        for i, detector in enumerate(results[0].detectors):
            datas = [
                result.results[fit]\
                    .query(f"detector == '{detector}' and correction == '{correction}'")
                for result in results
            ]

            self.plot_strategy.do_plot(datas, label=detector, color=self.config.colors[i])

        self._post_plot(fit, correction)

    def _post_plot(self, fit, correction):
        self.plot_strategy.style_plot(fit=fit, correction=correction, xticks=self.config.xticks)
        self.plot_strategy.save_plot(
            self.config.output_dir,
            f"{fit}_{correction}",
            suffix=self.config.file_suffix,
            file_ext=self.config.file_ext,
        )
