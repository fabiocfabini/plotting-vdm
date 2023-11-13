from itertools import product
from dataclasses import dataclass
from typing import Optional

import numpy as np
import matplotlib.pyplot as plt

from plotting_vdm.plotter.scan.base import Plotter
from plotting_vdm.plotter.config import PlotterCongig
from plotting_vdm.scan_results import ScanResults
from .strategy import CorrPlotStrategy


@dataclass
class CorrPlotter(Plotter):
    base_reference: str
    config: PlotterCongig
    plot_strategy: Optional[CorrPlotStrategy] = None

    def set_strategy(self, plot_strategy: CorrPlotStrategy):
        if not isinstance(plot_strategy, CorrPlotStrategy):
            raise TypeError(f"Expected CorrPlotStrategy, got {type(plot_strategy)}")

        self.plot_strategy = plot_strategy

    def plot(self, result: ScanResults):
        if self.plot_strategy is None:
            raise ValueError("Plot strategy not set")

        # NOTE: If corrections are not equal across every fit-detector pair, will this cause a bug?
        applied_corrections = result.corrections

        for fit, correction in product(result.fits, result.corrections):
            if correction == "noCorr":
                continue

            plt.clf()

            ref_correction = self.get_reference_correction(correction, applied_corrections)
            for i, detector in enumerate(result.detectors):
                data = result.results[fit].query(
                    f"detector == '{detector}' and correction == '{correction}'")
                ref = result.results[fit].query(
                    f"detector == '{detector}' and correction == '{ref_correction}'")

                if not ref["BCID"].equals(data["BCID"]):
                    bcid_filter = np.intersect1d(ref["BCID"], data["BCID"])

                    data = data[data["BCID"].isin(bcid_filter)].reset_index(drop=True)
                    ref = ref[ref["BCID"].isin(bcid_filter)].reset_index(drop=True)

                self.plot_strategy.do_plot(data, ref, label=detector, color=self.config.colors[i])

            self._post_plot(result, fit, correction, ref_correction)

    def get_reference_correction(self, correction: str, applied_corrections: list) -> str:
        base_ref_corr = self.base_reference
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

    def _post_plot(self, result: ScanResults, fit: str, correction: str, ref_correction: str):
        self.plot_strategy.style_plot(
            scan_name=result.name, fit=fit,
            correction=correction, difference=ref_correction.split("_")[-1]
        )

        self.plot_strategy.save_plot(
            self.config.output_dir/result.id_str,
            f"{fit}_{correction}",
            suffix=self.config.file_suffix,
            file_ext=self.config.file_ext
        )
