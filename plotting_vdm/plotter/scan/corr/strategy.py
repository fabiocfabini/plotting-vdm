from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from plotting_vdm.plotter.utils import TitleBuilder


@dataclass
class CorrPlotStrategy:
    latex: str
    quantity: str
    quantity_err: str
    output_folder_name: str

    axis_text: str = ""
    file_name_prepend: str = ""

    def do_plot(self, data: pd.DataFrame, ref: pd.DataFrame, *, label: str, color: str = "k"):
        ratio = (data[self.quantity] / ref[self.quantity] - 1) * 100
        ratio_err = np.abs(ratio) * np.sqrt(
            (data[self.quantity_err] / data[self.quantity])**2 +
            (ref[self.quantity_err] / ref[self.quantity])**2
        )

        plt.errorbar(x=data["BCID"], y=ratio, yerr=ratio_err, fmt="o", label=label, color=color)

    def style_plot(self, *, scan_name: str = "", fit: str = "", correction: str = "", difference: str = ""):
        title = TitleBuilder()\
                .set_scan_name(scan_name)\
                .set_fit(fit)\
                .set_correction(correction)\
                .set_axis(self.axis_text)\
                .set_info(f"Effect of {difference} on {self.latex}")\
                .build()
        plt.title(title)
        plt.xlabel("BCID")
        plt.ylabel(f"Effect of {difference} on {self.latex}")

        plt.grid()
        plt.legend(loc="best")

    def save_plot(self, ouput_dir: Path, file_name: str, *, suffix: str = "", file_ext: str = "png"):
        path = ouput_dir/"corr"/self.output_folder_name
        path.mkdir(parents=True, exist_ok=True)

        file_name = f"{self.file_name_prepend}{file_name}{suffix}.{file_ext}"

        plt.savefig(path/file_name)


@dataclass
class CapSigmaXCorrPlotStrategy(CorrPlotStrategy):
    latex: str = r"$\Sigma_X$"
    quantity: str = "CapSigma_X"
    quantity_err: str = "CapSigmaErr_X"
    output_folder_name: str = "capsigma"

    axis_text: str = "X Scan"
    file_name_prepend: str = "X_"

@dataclass
class CapSigmaYCorrPlotStrategy(CorrPlotStrategy):
    latex: str = r"$\Sigma_Y$"
    quantity: str = "CapSigma_Y"
    quantity_err: str = "CapSigmaErr_Y"
    output_folder_name: str = "capsigma"

    axis_text: str = "Y Scan"
    file_name_prepend: str = "Y_"

@dataclass
class PeakXCorrPlotStrategy(CorrPlotStrategy):
    latex: str = r"$\mathrm{Peak}_X$"
    quantity: str = "peak_X"
    quantity_err: str = "peakErr_X"
    output_folder_name: str = "peak"

    axis_text: str = "X Scan"
    file_name_prepend: str = "X_"

@dataclass
class PeakYCorrPlotStrategy(CorrPlotStrategy):
    latex: str = r"$\mathrm{Peak}_Y$"
    quantity: str = "peak_Y"
    quantity_err: str = "peakErr_Y"
    output_folder_name: str = "peak"

    axis_text: str = "Y Scan"
    file_name_prepend: str = "Y_"

@dataclass
class SigVisCorrPlotStrategy(CorrPlotStrategy):
    latex: str = r"$\sigma_{vis}$"
    quantity: str = "xsec"
    quantity_err: str = "xsecErr"
    output_folder_name: str = "sigvis"
