import numpy as np
import matplotlib.pyplot as plt

from plotting_vdm.scan_results import ScanResults
from plotting_vdm._typing import OneOrMany
from plotting_vdm.utils.title_builder import TitleBuilder
from plotting_vdm.utils.functions import match_bcids
from .base import PlotStrategy


class RatioPlotStrategy(PlotStrategy):
    def __init__(self, reference_detector:str, quantity: str, error: str, quantity_latex: str = "", **kwargs):
        super().__init__(**kwargs)
        self.reference_detector = reference_detector
        self.quantity = quantity
        self.error = error
        self.quantity_latex = quantity_latex if quantity_latex else quantity

        self.output_dir = self.output_dir/"ratio"
        self.xlabel = kwargs.get("xlabel", "BCID")

    def on_correction_loop_entry(self, results: OneOrMany[ScanResults], fit: str, correction: str) -> bool:
        plt.clf()

        return False

    def on_detector_loop(self, i, results: OneOrMany[ScanResults], fit: str, correction: str, detector: str):
        if detector == self.reference_detector:
            return

        data = results.filter_results_by(
            fit, correction, detector, quality=self.data_quality
        ).set_index("BCID")
        ref = results.filter_results_by(
            fit, correction, self.reference_detector, quality=self.data_quality
        ).set_index("BCID")
        data, ref = match_bcids(data, ref)

        yaxis = data[self.quantity] / ref[self.quantity]
        yerr = yaxis * np.sqrt(
            (data[self.error] / data[self.quantity]) ** 2
            + (ref[self.error] / ref[self.quantity]) ** 3
        )

        plt.errorbar(
            data.index,
            yaxis,
            yerr=yerr,
            label=f"{detector}/{self.reference_detector}",
            fmt=self.fmt,
            color=self.colors[i],
            markersize=self.markersize,
            elinewidth=self.elinewidth,
        )

    def on_correction_loop_exit(self, results: OneOrMany[ScanResults], fit, correction):
        title = TitleBuilder() \
                .set_fit(fit) \
                .set_correction(correction) \
                .set_info(f"Ratio of {self.quantity_latex}").build()

        plt.grid()
        plt.title(title)
        plt.xlabel(self.xlabel)
        plt.ylabel(f"Ratio of {self.quantity_latex}")
        plt.legend(loc=self.legend_loc, fontsize=self.legend_fontsize)
        plt.ticklabel_format(useOffset=False, axis="y")  # Prevent plt from adding offset to y axis

        path = self.output_dir/results.id_str/self.quantity/fit
        path.mkdir(parents=True, exist_ok=True)

        file = f"{correction}.png"
        plt.savefig(path/file)
