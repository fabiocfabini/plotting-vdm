from typing import Sequence
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from vdm_tools.io import ScanResults
from vdm_tools.plotting.utils import TitleBuilder, match_bcids
from vdm_tools.plotting import PlotContext
from vdm_tools.plotting import VdMPlotter, PerDetectorPlotter
from vdm_tools.plotting import StrategyPluginCore, StrategyMeta

plt.style.use("classic")
plt.rcParams["legend.numpoints"] = 1


def stats(values: np.ndarray, errors: np.ndarray) -> tuple:
    weights = 1/errors**2
    avg = np.average(values, weights=weights)
    error = np.sqrt(np.average((values-avg)**2, weights=weights))
    return avg, error

class RatioStrategy(StrategyPluginCore):
    """This strategy plots the specified data for a single scan per BCID.
    """
    def __init__(self, reference_detector: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reference_detector = reference_detector

    def plot(self, i: int, scan_results: ScanResults, plot_context: PlotContext) -> None:
        data = scan_results.filter_results_by(
            plot_context.current_fit,
            plot_context.current_correction,
            plot_context.current_detector,
            quality=self.data_quality,
        ).set_index("BCID")
        ref = scan_results.filter_results_by(
            plot_context.current_fit,
            plot_context.current_correction,
            self.reference_detector,
            quality=self.data_quality,
        ).set_index("BCID")
        data, ref = match_bcids(data, ref)

        yaxis = data[self.quantity] / ref[self.quantity]
        yerr = np.abs(yaxis) * np.sqrt(
            (data[self.error] / data[self.quantity]) ** 2
            + (ref[self.error] / ref[self.quantity]) ** 3
        )

        plt.errorbar(
            data.index,
            yaxis,
            yerr=yerr,
            label=f"{plot_context.current_correction}/{self.reference_detector}",
            fmt=self.meta.fmt,
            color=self.meta.colors[i],
            markersize=self.meta.markersize,
            elinewidth=self.meta.elinewidth,
        )

    def style(self, scan_results: ScanResults, plot_context: PlotContext) -> None:
        # Call the parent method if you want to keep the default styling
        super().style(scan_results, plot_context)

        title = TitleBuilder() \
                .set_fit(plot_context.current_fit) \
                .set_correction(plot_context.current_correction) \
                .set_info(f"Ratio of {self.latex}").build()

        plt.title(title)
        plt.xlabel("BCID")
        plt.ylabel(self.latex)
        plt.legend(loc=self.meta.legend_loc, fontsize=self.meta.legend_fontsize)


scan = ScanResults("/home/fabiocfabini/Desktop/CS/plotting-vdm/analysed_data/8381_11Nov22_114759_11Nov22_121408", ["DG"])
strat = RatioStrategy(
    "HFOC",
    "corr",
    "CapSigma_X",
    "CapSigmaErr_X",
    latex=r"$\Sigma_X$",
    data_quality="good",
    output_dir="/home/fabiocfabini/cernbox/www/plotts"
)
plotter = VdMPlotter(plot_strategy=strat)
plotter(scan)
strat = RatioStrategy(
    "HFOC",
    "corr",
    "CapSigma_Y",
    "CapSigmaErr_Y",
    latex=r"$\Sigma_Y$",
    data_quality="good",
    output_dir="/home/fabiocfabini/cernbox/www/plotts"
)
plotter = VdMPlotter(plot_strategy=strat)
plotter(scan)
# strat = RatioStrategy(
#     "HFOC",
#     "corr",
#     "peak_Y",
#     "peakErr_Y",
#     latex=r"$\mathrm{Peak}_Y$",
#     data_quality="good"
# )
# plotter = VdMPlotter(plot_strategy=strat)
# plotter(scan)
# strat = RatioStrategy(
#     "HFOC",
#     "corr",
#     "peak_X",
#     "peakErr_X",
#     latex=r"$\mathrm{Peak}_X$",
#     data_quality="good"
# )
# plotter = VdMPlotter(plot_strategy=strat)
# plotter(scan)
# strat = RatioStrategy(
#     "HFOC",
#     "corr",
#     "xsec",
#     "xsecErr",
#     latex=r"$\sigma_\mathrm{vis}$",
#     data_quality="good",
#     output_dir="/home/fabiocfabini/cernbox/www/plotts",
#     meta=StrategyMeta(colors=["b"]*len(scan.detectors))
# )
# plotter = VdMPlotter(plot_strategy=strat)
# plotter(scan)

class EvoStrategy(StrategyPluginCore):
    """This strategy plots the effect of a correction on a quantity.
    """
    def plot(self, i: int, scan_results: Sequence[ScanResults], plot_context: PlotContext) -> None:
        assert isinstance(scan_results, list)
        x_values = np.arange(1, len(scan_results)+1)
        y_values = np.empty(len(scan_results))
        y_errors = np.empty(len(scan_results))

        for j, result in enumerate(scan_results):
            data = result.filter_results_by(
                plot_context.current_fit,
                plot_context.current_correction,
                plot_context.current_detector,
                quality=self.data_quality
            )

            y_values[j], y_errors[j] = self.scan_stats(data[self.quantity], data[self.error])

        # Use detector for label only if we are not plotting
        label = plot_context.current_detector
        if plot_context.plotter.is_per_detector():
            label = ""

        plt.errorbar(
            x_values,
            y_values,
            yerr=y_errors,
            fmt=self.meta.fmt,
            color=self.meta.colors[i],
            label=label,
            markersize=self.meta.markersize,
            elinewidth=self.meta.elinewidth,
        )

        # Add the arrays to the plot context so that they can be used by the style method
        plot_context["x_values"] = x_values
        plot_context["y_values"] = y_values
        plot_context["y_errors"] = y_errors

    def style(self, scan_results: Sequence[ScanResults], plot_context: PlotContext) -> None:
        # Call the parent method if you want to keep the default styling
        super().style(scan_results, plot_context)

        builder = TitleBuilder() \
                .set_info(self.quantity) \
                .set_fit(plot_context.current_fit) \
                .set_correction(plot_context.current_correction)

        if plot_context.is_in_detector_loop():
            builder = builder.set_detector(plot_context.current_detector)
        title = builder.build()

        ticks = [result.name for result in scan_results]

        plt.xlim(0, len(scan_results)+1)
        plt.title(title)
        plt.xlabel("Scan Names")
        plt.ylabel(self.latex)
        plt.xticks(range(1, len(scan_results)+1), ticks, rotation=0)

        if plot_context.is_in_detector_loop():
            avg, error = self.scan_stats(plot_context["y_values"], plot_context["y_errors"])
            plt.axhline(avg, color="red", label=f"{self.latex} {avg:.2f} +/- {error:.2f}. ({error/avg*100:.2f} %)")
            plt.axhline(avg-error, color="orange", linestyle="--", alpha=0.9)
            plt.axhline(avg+error, color="orange", linestyle="--", alpha=0.9)
            plt.fill_between(plt.xlim(), avg-error, avg+error, color="orange", alpha=0.3)

        plt.legend(loc=self.meta.legend_loc, fontsize=self.meta.legend_fontsize)


fill_8999 = {
    # "8999_28Jun23_222504_28Jun23_223127": "emit1",
    "8999_28Jun23_230143_28Jun23_232943": "VdM1",
    # "8999_28Jun23_235337_29Jun23_001656": "ds1",
    "8999_29Jun23_004658_29Jun23_011220": "BI1",
    "8999_29Jun23_013851_29Jun23_020425": "BI2",
    "8999_29Jun23_023227_29Jun23_025502": "VdM2",
    "8999_29Jun23_073830_29Jun23_080352": "VdM3",
    # "8999_29Jun23_083200_29Jun23_085852": "os1",
    "8999_29Jun23_092415_29Jun23_094738": "VdM4",
    # "8999_29Jun23_101314_29Jun23_103550": "ds2",
    "8999_29Jun23_110004_29Jun23_112226": "VdM5",
    # "8999_29Jun23_114555_29Jun23_115221": "emit2",
    "8999_29Jun23_123257_29Jun23_125514": "VdM6",
    # "8999_29Jun23_211111_29Jun23_211737": "emit3",
}

results_path = Path("/home/fabiocfabini/cernbox/www/8999_output")
if not results_path.exists():
    raise ValueError(f"Path {results_path} does not exist")
res_path = results_path/"analysed_data"
all_scans = [ScanResults(path, fits=["DG"], name=fill_8999[path.stem]) for path in res_path.glob("8999*") if path.stem in fill_8999]
plotter = PerDetectorPlotter()
all_scans.sort(key=lambda s: s.start)

strategy = EvoStrategy(
    "evo",
    "xsec",
    "xsecErr",
    latex=r"$\sigma_\mathrm{vis}$",
    data_quality="good",
    output_dir="./plots_8999",
    scan_stats=stats,
    meta=StrategyMeta(
        fmt="s",
        markersize=8,
        elinewidth=0.5,
        colors=["b"]*len(all_scans),
    )
)
plotter.plot_strategy = strategy
plotter(all_scans)
print(f"Plots saved in {results_path/'../plots'}")
