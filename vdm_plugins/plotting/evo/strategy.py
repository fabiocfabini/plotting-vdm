from typing import Sequence

import numpy as np
import matplotlib.pyplot as plt


from vdm_tools.io import ScanResults
from vdm_tools.plotting.utils import TitleBuilder
from vdm_tools.plotting.strategy import StrategyPluginCore
from vdm_tools.plotting import PlotContext


class EvoStrategy(StrategyPluginCore):
    """This plugin provides a strategy for plotting the evolution
    of a quantity as a function of scan number.
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
