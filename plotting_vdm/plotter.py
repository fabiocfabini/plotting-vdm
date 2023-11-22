from collections.abc import Sequence
from typing import Tuple, List

from plotting_vdm.scan_results import ScanResults
from plotting_vdm._typing import OneOrMany
from .common.strategies.base import PlotStrategy


class VdMPlotter:
    """Skeleton class for most vdm related plots.
    Given OneOrMany[ScanResults] it will loop over all fits,
    corrections and detectors and call the corresponding methods
    of the set PlotStrategy.

    Parameters
    ----------
    plot_strategy : PlotStrategy, optional
        Instance of PlotStrategy. Must be set before calling `plot` method.

    Raises
    ------
    ValueError
        If no plot strategy is set upon calling `plot` method.
    TypeError
        If `results` is not ScanResults or Sequence[ScanResults].

    Examples
    --------
    # TODO: Add example
    """
    def __init__(self, plot_strategy: PlotStrategy = None):
        self.plot_strategy = plot_strategy

    def __call__(self, results: OneOrMany[ScanResults]):
        self.plot(results)

    def plot(self, results: OneOrMany[ScanResults]):
        """Generates all the plots for the given OneOrMany[ScanResults].
        Follows the logic of the underlying PlotStrategy. This means that
        the PlotStrategy must be aware of the structure of the ScanResults
        and create the plot logic accordingly. This acts as a mere skeleton
        for the plotting logic.

        Parameters
        ----------
        results : OneOrMany[ScanResults]
            ScanResults to plot.
        """
        if self.plot_strategy is None:
            raise ValueError("No plot strategy set")

        fits, corrections, detectors = self._get_loop_iterables(results)

        for fit in fits:
            for correction in corrections:
                skip_correction = self.plot_strategy.on_correction_loop_entry(results, fit, correction)

                if skip_correction:
                    continue

                for i, detector in enumerate(detectors):
                    self.plot_strategy.on_detector_loop(i, results, fit, correction, detector)

                self.plot_strategy.on_correction_loop_exit(results, fit, correction)

    def _get_loop_iterables(self, results: OneOrMany[ScanResults]) -> Tuple[List[str], ...]:
        if isinstance(results, Sequence) and not isinstance(results, str):
            result = next(iter(results))
            return result.fits, result.corrections, result.detectors

        if isinstance(results, ScanResults):
            return results.fits, results.corrections, results.detectors

        raise TypeError("plot method expects ScanResults or Sequence[ScanResults]")
