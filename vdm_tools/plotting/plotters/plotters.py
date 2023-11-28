from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Sequence, Callable, Union

from vdm_tools.io import ScanResults
from .context import PlotContext
from ..strategy.strategy import StrategyPluginCore


def _run_filters(which: str) -> Callable:
    """Decorator that runs the filters before calling the decorated function.
    The decorated function will be called only if all filters fail to filter
    the current value of the attribute.

    Parameters
    ----------
    which : str
        The name of the attribute that will be used to run the filters.
        Allowed values are: "fit", "detector", "correction".

    Returns
    -------
    Callable
        The decorated function.
    """
    def wrapper(function):
        def inner(self: VdMPlotter, *args, **kwargs):
            if not self._to_filter(which): # pylint: disable=protected-access
                function(self, *args, **kwargs)
        return inner
    return wrapper


class RunFiltersMeta(type):
    """Decorates the METHODS_TO_FILTER methods in a VdMPlotter class
    with the _run_filters decorator.
    """
    # Maps the 'which' argument of the _run_filters decorator
    # to the name of the method that will be decorated.
    METHODS_TO_FILTER = {
        "fit": "_fit_body",
        "correction": "_correction_body",
        "detector": "_detector_body"
    }

    def __new__(mcs, name, bases, attrs):
        for which, method in mcs.METHODS_TO_FILTER.items():
            # Not all subclasses of VdMPlotter will have all the methods
            # that are decorated with the _run_filters decorator. This is
            # because they may choose to not override some of the methods.
            if method in attrs:
                attrs[method] = _run_filters(which)(attrs[method])
        return super().__new__(mcs, name, bases, attrs)


# pylint: disable=W0238
@dataclass
class VdMPlotter(metaclass=RunFiltersMeta):
    """Base Plotter class for VdM plots.
    This plotter will loop over all fits, corrections and detectors calling
    the appropriate methods of the set plot strategy. The plotter will create
    one figure per fit and correction (meaning all detectors will be plotted
    in the same figure).

    Parameters
    ----------
    plot_strategy : StrategyPluginCore, optional
        Instance of StrategyPluginCore. This attribute must be set before calling
        the `__call__` method.
    plot_context : PlotContext, default_factory=PlotContext
        The context of the plot. This attribute is used to pass information
        between the different methods of the plot strategy.

    Raises
    ------
    ValueError
        If no plot strategy is set upon calling `__call__` method.
    TypeError
        If `scan_results` is not ScanResults or Sequence[ScanResults].
    """
    plot_context: PlotContext = field(default_factory=PlotContext)
    plot_strategy: StrategyPluginCore = None

    def __call__(self, scan_results: Union[ScanResults, Sequence[ScanResults]], keep_context: bool = False) -> None:
        if not keep_context:
            self.plot_context.clear()
        self.plot_context.reset()
        self.plot_context["plotter"] = self

        if self.plot_strategy is None:
            raise ValueError("Plot strategy has not been set.")

        if isinstance(scan_results, Sequence) and not isinstance(scan_results, str):
            if self.plot_strategy.run_with_list:
                self.run(scan_results)
            else:
                for result in scan_results:
                    self.run(result)
        elif isinstance(scan_results, ScanResults):
            self.run(scan_results)
        else:
            raise TypeError("plot method expects ScanResults or Sequence[ScanResults]")

    def run(self, scan_results: Union[ScanResults, Sequence[ScanResults]]) -> None:
        """Method that runs the plotting procedure.

        Parameters
        ----------
        scan_results : ScanResults or Sequence[ScanResults]
            The plot strategy must be aware of the the type of this argument.

        Notes
        -----
        This method should not be called directly. Instead, it should be called
        by the `__call__` method. This is done to ensure that the plot context
        is reset before running the plotting procedure as well as to ensure that
        the plot strategy has been set.
        """
        fits = self._get_loop_iterable("fits", scan_results)
        for fit in fits:
            self.plot_context.current_fit = fit
            self._fit_body(scan_results)

        # Remember to reset the current fit
        # once the correction loop is finished.
        self.plot_context.current_fit = ""

    def is_per_detector(self) -> bool:
        """Returns True if the plotter is per detector.
        """
        return isinstance(self, PerDetectorPlotter)

    def _fit_body(self, scan_results: Union[ScanResults, Sequence[ScanResults]]) -> None:
        corrections = self._get_loop_iterable("corrections", scan_results)
        for correction in corrections:
            self.plot_context.current_correction = correction
            self._correction_body(scan_results)

        # Remember to reset the current correction
        # once the correction loop is finished.
        self.plot_context.current_correction = ""

    def _correction_body(self, scan_results: Union[ScanResults, Sequence[ScanResults]]) -> None:
        self.plot_strategy.prepare(scan_results, self.plot_context)

        detectors = self._get_loop_iterable("detectors", scan_results)
        for i, detector in enumerate(detectors):
            self.plot_context.current_detector = detector
            self._detector_body(i, scan_results)

        # Remember to reset the current detector
        # once the correction loop is finished.
        self.plot_context.current_detector = ""

        self.plot_strategy.style(scan_results, self.plot_context)
        self.plot_strategy.save(scan_results, self.plot_context)

    def _detector_body(self, i: int, scan_results: Union[ScanResults, Sequence[ScanResults]]) -> None:
        self.plot_strategy.plot(i, scan_results, self.plot_context)

    @staticmethod
    def _get_loop_iterable(which: str, scan_results: Union[ScanResults, Sequence[ScanResults]]) -> List[str]:
        """Returns an iterable that will be used to loop over the given scan results.

        Parameters
        ----------
        which : str
            The name of in scan results that will be used to get the iterable.
            Allowed values are: "fit", "detector", "correction".

        scan_results : ScanResults or Sequence[ScanResults]
            The scan results to loop over.

        Returns
        -------
        List[str]
            The iterable that will be used to loop over the fits, corrections or detectors
            of the given scan results.

        Raises
        ------
        TypeError
            If `scan_results` is not ScanResults or Sequence[ScanResults].
        """
        if isinstance(scan_results, Sequence) and not isinstance(scan_results, str):
            result = next(iter(scan_results))
            return getattr(result, which)

        if isinstance(scan_results, ScanResults):
            return getattr(scan_results, which)

        raise TypeError("plot method expects ScanResults or Sequence[ScanResults]")

    def _to_filter(self, which: str) -> bool:
        filters = getattr(self.plot_strategy, f"{which}_filters")
        value_to_filter = getattr(self.plot_context, f"current_{which}")

        return any((
            filter(value_to_filter, self.plot_context)
            for filter in filters
        ))


class PerDetectorPlotter(VdMPlotter):
    def _correction_body(self, scan_results: Union[ScanResults, Sequence[ScanResults]]) -> None:
        detectors = self._get_loop_iterable("detectors", scan_results)
        for i, detector in enumerate(detectors):
            self.plot_context.current_detector = detector
            self._detector_body(i, scan_results)
        self.plot_context.current_detector = None

    def _detector_body(self, i, scan_results: Union[ScanResults, Sequence[ScanResults]]) -> None:
        self.plot_strategy.prepare(scan_results, self.plot_context)
        self.plot_strategy.plot(i, scan_results, self.plot_context)
        self.plot_strategy.style(scan_results, self.plot_context)
        self.plot_strategy.save(scan_results, self.plot_context)
