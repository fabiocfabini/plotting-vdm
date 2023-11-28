from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Callable, Sequence, Union, Tuple, overload
from pathlib import Path

from numpy.typing import ArrayLike

import matplotlib.pyplot as plt

from vdm_tools.io import ScanResults
from ..plotters.plotters import PlotContext
from .meta import StrategyMeta


# pylint: disable=W0613
class StrategyPluginRegistry(type):
    """Metaclass that registers all subclasses of `StrategyPluginCore` in a dictionary."""
    registered_strategies: Dict[str, StrategyPluginCore] = {}

    def __init__(cls, name, bases, attrs):
        super().__init__(cls)
        if name != "StrategyPluginCore":
            StrategyPluginRegistry.registered_strategies[name] = cls


@dataclass
class StrategyPluginCore(metaclass=StrategyPluginRegistry):
    """Contract for all plot strategies.
    A plot strategy is responsible for:
        - Preparing the plot (done via the `prepare` method). For most strategies, this
        means clearing the previous figure in order to start with a clean slate.
        - Plotting the data (done via the `plot` method). This is where the actual plotting happens.
        - Styling the plot (done via the `style` method). This is where the plot is styled.
        - Saving the plot (done via the `save` method). This is where the plot is saved to disk.
        Unless you want to save the plot in a different format, you should not need to override
        this method.
    This class provides default implementations for all these methods except `plot`.

    Parameters
    ----------
    id : str
        An identifier for the plot strategy. The value of this attribute will be used to
        create a subdirectory in the output directory.
    quantity : str
        The quantity that will be plotted. This value must be one of the columns of the
        ScanResults dataframe. The value of this attribute will be used to create a
        subdirectory in the output directory.
    error : str
        The error that will be plotted. This value must be one of the columns of the
        ScanResults dataframe and it should correspond to the error of the quantity.
    latex : str, default=""
        The latex representation of the quantity. This value could be used for many
        purposes, such as the title of the plot.
    data_quality : str, default="as_is"
        The data quality that will be used to filter the data. This value must be one of
        'as_is', 'good', 'bad' as specified in the ScanResults instance.
    output_dir : Path or str, default=Path("./plots")
        The directory where the plots will be saved. If a string is passed, it will be
        converted to a Path object.
    fit_filters, detector_filters, correction_filters :
        List[Callable[[str, PlotContext], bool]], default_factory=list
        A list of filters that will be applied to the fit, detector and correction.
        These filters will decide wether or nor to skip the current fit, detector or
        correction. If any of the filters returns True the value will be skipped.
    scan_stats : Callable[[ArrayLike, ArrayLike], Tuple[float, float]], default_factory=mean_std
        A function that computes the statistics of the scan. The function should take
        two arguments:
            - The values of the specific quantity
            - The errors of the specific quantity
        The function should return a tuple of two floats:
            - The first will be considered the expected value of the quantity
            - The second will be considered the deviation of the expected value
    meta : StrategyMeta, default_factory=StrategyMeta
        The meta information of the strategy.

    Attributes
    ----------
    run_with_list : bool, default=False
        A flag that indicates whether or not the strategy should be run with a list of
        ScanResults. If this flag is set to True, then the strategy will be run with a
        list of ScanResults. Otherwise, the strategy will be run with a single ScanResults.
    """
    run_with_list: bool = field(default=False, init=False)
    id: str
    quantity: str
    error: str
    latex: str = ""
    data_quality: str = "as_is"
    output_dir: Path = Path("./plots")
    fit_filters: List[Callable[[str, PlotContext], bool]] = field(default_factory=list)
    detector_filters: List[Callable[[str, PlotContext], bool]] = field(default_factory=list)
    correction_filters: List[Callable[[str, PlotContext], bool]] = field(default_factory=list)
    scan_stats: Callable[[ArrayLike, ArrayLike], Tuple[float, float]] = field(
        default_factory=lambda: lambda val, err: (val.mean(), val.std())
    )
    meta: StrategyMeta = field(default_factory=StrategyMeta)

    def __post_init__(self):
        if not isinstance(self.output_dir, Path):
            self.output_dir = Path(self.output_dir)
        self.output_dir = self.output_dir/self.id

    @overload
    def prepare(self, scan_results: ScanResults, plot_context: PlotContext) -> None: ...
    @overload
    def prepare(self, scan_results: Sequence[ScanResults], plot_context: PlotContext) -> None: ...
    def prepare(self, scan_results, plot_context: PlotContext) -> None:
        """Method that is called before the actual plotting starts.
        It is normally used to clear the previous figure.

        Parameters
        ----------
        scan_results : ScanResults or Sequence[ScanResults]
            The scan results that will be plotted.
        plot_context : PlotContext
            The context of the plot up to this point.

        Notes
        -----
            Be aware of the type of scan_results. When creating
            a new plot strategy, it is your responsibility to know
            how to interact this argument.
        """
        plt.clf()

    @overload
    def plot(self, i: int, scan_results: ScanResults, plot_context: PlotContext) -> None: ...
    @overload
    def plot(self, i: int, scan_results: Sequence[ScanResults], plot_context: PlotContext) -> None: ...
    def plot(self, i: int, scan_results, plot_context: PlotContext) -> None:
        """Method that is called to plot the data.

        Parameters
        ----------
        i : int
            The index of the current detector.
        scan_results : ScanResults or Sequence[ScanResults]
            The scan results that will be plotted.
        plot_context : PlotContext
            The context of the plot up to this point.

        Notes
        -----
            Be aware of the type of scan_results. When creating
            a new plot strategy, it is your responsibility to know
            how to interact this argument.
        """
        raise NotImplementedError

    @overload
    def style(self, scan_results: ScanResults, plot_context: PlotContext) -> None: ...
    @overload
    def style(self, scan_results: Sequence[ScanResults], plot_context: PlotContext) -> None: ...
    def style(self, scan_results, plot_context: PlotContext) -> None:
        """Method that is called to style the plot.

        Parameters
        ----------
        scan_results : ScanResults or Sequence[ScanResults]
            The scan results that will be plotted.
        plot_context : PlotContext
            The context of the plot up to this point.

        Notes
        -----
            Be aware of the type of scan_results. When creating
            a new plot strategy, it is your responsibility to know
            how to interact this argument.
        """
        plt.grid(True)
        # Do not use offset for the y-axis
        plt.ticklabel_format(useOffset=False, axis="y")

    @overload
    def save(self, scan_results: ScanResults, plot_context: PlotContext) -> None: ...
    @overload
    def save(self, scan_results: Sequence[ScanResults], plot_context: PlotContext) -> None: ...
    def save(self, scan_results, plot_context: PlotContext) -> None:
        """Method that is called after the actual plotting is done.
        It is normally used to save the figure.

        Parameters
        ----------
        scan_results : ScanResults or Sequence[ScanResults]
            The scan results that will be plotted.
        plot_context : PlotContext
            The context of the plot up to this point.

        Notes
        -----
            Be aware of the type of scan_results. When creating
            a new plot strategy, it is your responsibility to know
            how to interact this argument.
        """
        path = self.__compute_path(scan_results, plot_context)
        path.mkdir(parents=True, exist_ok=True)

        file = f"{plot_context.current_correction}.png"
        plt.savefig(path/file)

    def __compute_path(self, scan_results: Union[ScanResults, Sequence[ScanResults]], plot_context: PlotContext) -> Path:
        """Method that computes the path where the plot will be saved.

        Parameters
        ----------
        scan_results : ScanResults or Sequence[ScanResults]
            The scan results that will be plotted.

        Returns
        -------
        Path
            The path where the plot will be saved.
        """
        fill_range_str = self._compute_fill_range(scan_results)

        path = self.output_dir/fill_range_str/self.quantity
        path = self._append_per_detector_path(path, plot_context)
        return path/plot_context.current_fit/plot_context.current_detector

    @staticmethod
    def _append_per_detector_path(path: Path, plot_context: PlotContext) -> Path:
        """Method that adds the appends the per detector path to the given path.

        Parameters
        ----------
        path : Path
            The path where the plot will be saved.
        plot_context : PlotContext
            The context of the plot up to this point.

        Returns
        -------
        Path
            The path where the plot will be saved. With the per detector path appended.
        """
        # If the value of current_detector is an empty string, then
        # we have gone outside the detector loop. In this case, we
        # do not want to append the per detector path.
        if plot_context.current_detector == "":
            return path

        return path/"separete"

    @staticmethod
    def _compute_fill_range(scan_results: Union[ScanResults, Sequence[ScanResults]]) -> str:
        """Method that computes the fill range of the given scan results and returns
        a string representation of it. The string representation is of the form:
            - "<max_fill>-<min_fill>" (e.g. 8381-8382): if scan_results is a sequence
              of ScanResults
            - "scan_results.id_str": if scan_results is a single ScanResults

        Parameters
        ----------
        scan_results : ScanResults or Sequence[ScanResults]
            The scan results that will be plotted.

        Returns
        -------
        str
            The string representation of the fill range.
        """
        if isinstance(scan_results, ScanResults):
            return scan_results.id_str

        # At this point, we assume scan_results is a sequence of ScanResults
        max_fill = max(scan_results, key=lambda scan: scan.fill_number).fill_number
        min_fill = min(scan_results, key=lambda scan: scan.fill_number).fill_number

        if max_fill == min_fill:
            return str(max_fill)

        return f"{min_fill}-{max_fill}"



