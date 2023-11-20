import numpy as np
import matplotlib.pyplot as plt

from plotting_vdm.scan_results import ScanResults
from plotting_vdm._typing import OneOrMany
from plotting_vdm.utils.title_builder import TitleBuilder
from plotting_vdm.utils.functions import match_bcids
from .base import PlotStrategy


class CorrPlotStrategy(PlotStrategy):
    def __init__(self, base_correction:str, quantity: str, error: str, quantity_latex: str = "", **kwargs):
        super().__init__(**kwargs)
        self.base_correction = base_correction
        self.quantity = quantity
        self.error = error
        self.quantity_latex = quantity_latex if quantity_latex else quantity

        self.output_dir = self.output_dir/"corr"
        self.xlabel = kwargs.get("xlabel", "BCID")

    def on_correction_loop_entry(self, results: OneOrMany[ScanResults], fit: str, correction: str) -> bool:
        if correction == "no_corr":
            return True

        plt.clf()

        self.context["reference"] = self.get_reference_correction(correction, results.corrections)

        return False

    def on_detector_loop(self, i, results: OneOrMany[ScanResults], fit: str, correction: str, detector: str):
        data = results.filter_results_by(
            fit, correction, detector, quality=self.data_quality
        ).set_index("BCID")
        ref = results.filter_results_by(
            fit, self.context["reference"], detector, quality=self.data_quality
        ).set_index("BCID")
        data, ref = match_bcids(data, ref)

        yaxis = (data[self.quantity] / ref[self.quantity] - 1) * 100
        yerr = yaxis * np.sqrt(
            (data[self.error] / data[self.quantity]) ** 2
            + (ref[self.error] / ref[self.quantity]) ** 3
        )

        plt.errorbar(
            data.index,
            yaxis,
            yerr=yerr,
            label=detector,
            fmt=self.fmt,
            color=self.colors[i],
            markersize=self.markersize,
        )

    def on_correction_loop_exit(self, results: OneOrMany[ScanResults], fit: str, correction: str):
        title = TitleBuilder() \
                .set_fit(fit) \
                .set_correction(correction) \
                .set_info(f"Effect of {correction.split('_')[-1]} on {self.quantity_latex}").build()

        plt.grid()
        plt.title(title)
        plt.xlabel(self.xlabel)
        plt.ylabel(f"Effect of {correction.split('_')[-1]} on {self.quantity_latex}")
        plt.legend(loc=self.legend_loc, fontsize=self.legend_fontsize)
        plt.ticklabel_format(useOffset=False, axis="y")  # Prevent plt from adding offset to y axis

        path = self.output_dir/results.id_str/self.quantity/fit
        path.mkdir(parents=True, exist_ok=True)

        file = f"{correction}.png"
        plt.savefig(path/file)

    def get_reference_correction(self, correction: str, applied_corrections: list) -> str:
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
