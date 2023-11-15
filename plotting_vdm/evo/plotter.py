from typing import Sequence

from plotting_vdm.scan_results import ScanResults
from .strategies.base import PlotStrategy


class EvoPlotter:
    def __init__(self, plot_strategy: PlotStrategy = None):
        self.plot_strategy = plot_strategy

    def __call__(self, results: Sequence[ScanResults]):
        self.plot(results)

    def plot(self, results: Sequence[ScanResults]):
        if self.plot_strategy is None:
            raise NotImplementedError("No plot strategy set")

        fits = results[0].fits
        detectors = results[0].detectors
        corrections = results[0].corrections

        for fit in fits:

            for correction in corrections:
                self.plot_strategy.on_correction_loop_entry(results, fit, correction)

                for i, detector in enumerate(detectors):
                    self.plot_strategy.on_detector_loop(i, results, fit, correction, detector)

                self.plot_strategy.on_correction_loop_exit(results, fit, correction)