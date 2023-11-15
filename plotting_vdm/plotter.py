from plotting_vdm.scan_results import ScanResults
from plotting_vdm._typing import OneOrMany
from .common.strategies.base import PlotStrategy


class VdMPlotter:
    def __init__(self, plot_strategy: PlotStrategy = None):
        self.plot_strategy = plot_strategy

    def __call__(self, results: OneOrMany[ScanResults]):
        self.plot(results)

    def plot(self, results: OneOrMany[ScanResults]):
        if self.plot_strategy is None:
            raise NotImplementedError("No plot strategy set")

        if isinstance(results, list):
            fits = results[0].fits
            detectors = results[0].detectors
            corrections = results[0].corrections
        elif isinstance(results, ScanResults):
            fits = results.fits
            detectors = results.detectors
            corrections = results.corrections
        else:
            raise TypeError("plot method expects ScanResults or List[ScanResults]")

        for fit in fits:
            for correction in corrections:
                skip_correction = self.plot_strategy.on_correction_loop_entry(results, fit, correction)

                if skip_correction:
                    continue

                for i, detector in enumerate(detectors):
                    self.plot_strategy.on_detector_loop(i, results, fit, correction, detector)

                self.plot_strategy.on_correction_loop_exit(results, fit, correction)