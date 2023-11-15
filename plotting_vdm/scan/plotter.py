from plotting_vdm.scan_results import ScanResults
from plotting_vdm.scan.strategies.base import PlotStrategy



class ScanPlotter:
    def __init__(self, plot_strategy: PlotStrategy = None):
        self.plot_strategy = plot_strategy

    def __call__(self, results: ScanResults):
        self.plot(results)

    def plot(self, results: ScanResults):
        if self.plot_strategy is None:
            raise NotImplementedError("No plot strategy set")

        for fit in results.fits:

            for correction in results.corrections:
                skip_correction = self.plot_strategy.on_correction_loop_entry(results, fit, correction)

                if skip_correction:
                    continue

                for i, detector in enumerate(results.detectors):
                    self.plot_strategy.on_detector_loop(i, results, fit, correction, detector)

                self.plot_strategy.on_correction_loop_exit(results, fit, correction)