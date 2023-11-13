from itertools import product
from dataclasses import dataclass
from typing import Optional

import numpy as np
import matplotlib.pyplot as plt

from plotting_vdm.plotter.scan.base import Plotter
from plotting_vdm.plotter.config import PlotterCongig
from plotting_vdm.scan_results import ScanResults
from .strategy import RatioPlotStrategy


@dataclass
class RatioPlotter(Plotter):
    reference_detector: str
    config: PlotterCongig
    plot_strategy: Optional[RatioPlotStrategy] = None

    def set_strategy(self, plot_strategy: RatioPlotStrategy):
        if not isinstance(plot_strategy, RatioPlotStrategy):
            raise TypeError(f"Expected RatioPlotStrategy, got {type(plot_strategy)}")

        self.plot_strategy = plot_strategy

    def plot(self, result: ScanResults):
        if self.plot_strategy is None:
            raise ValueError("Plot strategy not set")

        for fit, correction in product(result.fits, result.corrections):

            plt.clf()

            for i, detector in enumerate(result.detectors):
                if detector == self.reference_detector:
                    continue

                data = result.results[fit].query(
                    f"detector == '{detector}' and correction == '{correction}'")
                ref  = result.results[fit].query(
                    f"detector == '{self.reference_detector}' and correction == '{correction}'")

                if not ref["BCID"].equals(data["BCID"]):
                    bcid_filter = np.intersect1d(ref["BCID"], data["BCID"])

                    data = data[data["BCID"].isin(bcid_filter)].reset_index(drop=True)
                    ref = ref[ref["BCID"].isin(bcid_filter)].reset_index(drop=True)

                self.plot_strategy.do_plot(data, ref,
                    label=f"{detector}/{self.reference_detector}",
                    color=self.config.colors[i]
                )

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
