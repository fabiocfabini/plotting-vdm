import matplotlib.pyplot as plt

import numpy as np

from vdm_tools.io import ScanResults
from vdm_tools.plotting.utils import TitleBuilder
from vdm_tools.plotting.strategy import StrategyPluginCore
from vdm_tools.plotting import PlotContext
from vdm_tools.plotting.utils import match_bcids


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
