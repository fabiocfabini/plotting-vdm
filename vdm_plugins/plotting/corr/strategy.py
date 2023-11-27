import matplotlib.pyplot as plt

import numpy as np

from vdm_tools.io import ScanResults
from vdm_tools.plotting.utils import TitleBuilder
from vdm_tools.plotting.strategy import StrategyPluginCore
from vdm_tools.plotting import PlotContext
from vdm_tools.plotting.utils import match_bcids


class CorrStrategy(StrategyPluginCore):
    """This strategy plots the effect of a correction on a quantity.
    """
    def __init__(self, base_correction: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_correction = base_correction

    def prepare(self, scan_results: ScanResults, plot_context: PlotContext) -> None:
        # Call the parent method if you want to keep the default preparation
        super().prepare(scan_results, plot_context)

        plot_context["reference"] = self.get_reference_correction(
            plot_context.current_correction, scan_results.corrections
        )

    def plot(self, i: int, scan_results: ScanResults, plot_context: PlotContext) -> None:
        data = scan_results.filter_results_by(
            plot_context.current_fit,
            plot_context.current_correction,
            plot_context.current_detector,
            quality=self.data_quality,
        ).set_index("BCID")
        ref = scan_results.filter_results_by(
            plot_context.current_fit,
            plot_context["reference"],
            plot_context.current_detector,
            quality=self.data_quality,
        ).set_index("BCID")
        data, ref = match_bcids(data, ref)

        yaxis = (data[self.quantity] / ref[self.quantity] - 1) * 100
        yerr = np.abs(yaxis) * np.sqrt(
            (data[self.error] / data[self.quantity]) ** 2
            + (ref[self.error] / ref[self.quantity]) ** 3
        )

        plt.errorbar(
            data.index,
            yaxis,
            yerr=yerr,
            label=plot_context.current_detector,
            fmt=self.meta.fmt,
            color=self.meta.colors[i],
            markersize=self.meta.markersize,
            elinewidth=self.meta.elinewidth,
        )

    def style(self, scan_results: ScanResults, plot_context: PlotContext) -> None:
        # Call the parent method if you want to keep the default styling
        super().style(scan_results, plot_context)

        last_currection = plot_context.current_correction.split("_")[-1]
        title = TitleBuilder() \
                .set_fit(plot_context.current_fit) \
                .set_correction(plot_context.current_correction) \
                .set_info(f"Effect of {last_currection} on {self.latex}") \
                .build()

        plt.title(title)
        plt.xlabel("BCID")
        plt.ylabel(f"Effect of {last_currection} on {self.latex}")
        plt.legend(loc=self.meta.legend_loc, fontsize=self.meta.legend_fontsize)

    def get_reference_correction(self, correction: str, applied_corrections: list) -> str:
        """Get the reference correction for the effect plot.
        This is the correction that is applied before the correction
        that is being plotted.

        Parameters
        ----------
        correction : str
            The correction that is being plotted.
        applied_corrections : list
            The list of corrections that are applied to the data.

        Returns
        -------
        str
            The reference correction.
        """
        base_ref_corr = self.base_correction
        keep_looking = True
        tmp_corr = correction
        while keep_looking:
            if len(tmp_corr.split("_")) != 1:
                ref_corr = tmp_corr.replace("_" + tmp_corr.split("_")[-1], "")
            else:
                ref_corr = base_ref_corr
            if ref_corr in applied_corrections:
                keep_looking = False
            else:
                tmp_corr = ref_corr
            if (ref_corr == base_ref_corr) and (base_ref_corr not in applied_corrections):
                raise ValueError(f"""{base_ref_corr} is not in correction dictionary.
                                 Impossible to make correction effect plot
                                Please add {base_ref_corr} to correction dictionary""")

        return ref_corr
