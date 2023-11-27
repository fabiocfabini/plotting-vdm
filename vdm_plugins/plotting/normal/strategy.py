import matplotlib.pyplot as plt

from vdm_tools.io import ScanResults
from vdm_tools.plotting.utils import TitleBuilder
from vdm_tools.plotting.strategy import StrategyPluginCore
from vdm_tools.plotting import PlotContext


class NormalStrategy(StrategyPluginCore):
    """This strategy plots the specified data for a single scan per BCID.
    """
    def plot(self, i: int, scan_results: ScanResults, plot_context: PlotContext) -> None:
        data = scan_results.filter_results_by(
            plot_context.current_fit,
            plot_context.current_correction,
            plot_context.current_detector,
            quality=self.data_quality,
        )

        # Use detector for label only if we are not plotting per detector
        label = plot_context.current_detector
        if plot_context.plotter.is_per_detector():
            label = ""

        plt.errorbar(
            data["BCID"],
            data[self.quantity],
            yerr=data[self.error],
            label=label,
            fmt=self.meta.fmt,
            color=self.meta.colors[i],
            markersize=self.meta.markersize,
            elinewidth=self.meta.elinewidth,
        )

    def style(self, scan_results: ScanResults, plot_context: PlotContext) -> None:
        # Call the parent method if you want to keep the default styling
        super().style(scan_results, plot_context)

        builder = TitleBuilder() \
                .set_fit(plot_context.current_fit) \
                .set_correction(plot_context.current_correction) \
                .set_info(scan_results.name)

        if plot_context.is_in_detector_loop():
            builder = builder.set_detector(plot_context.current_detector)
        title = builder.build()

        plt.title(title)
        plt.xlabel("BCID")
        plt.ylabel(self.latex)
        if not plot_context.plotter.is_per_detector():
            plt.legend(loc=self.meta.legend_loc, fontsize=self.meta.legend_fontsize)
