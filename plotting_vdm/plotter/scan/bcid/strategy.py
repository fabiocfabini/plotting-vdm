from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from plotting_vdm.plotter.utils import TitleBuilder


def _set_current_detector(method):
    def wrapper(self: BCIDPlotStrategy, data: pd.DataFrame, *args, **kwargs):
        if self.plot_per_detector:
            self.current_detector = data["detector"].unique().item()

        return method(self, data, *args, **kwargs)

    return wrapper


@dataclass
class BCIDPlotStrategy:
    latex: str
    quantity: str
    output_folder_name: str
    plot_per_detector: bool

    quantity_err: str = ""
    axis_text: str = ""
    file_name_prepend: str = ""

    def __post_init__(self):
        self.current_detector = ""

    @property
    def plot_per_detector(self) -> bool:
        return self.plot_per_detector


    @_set_current_detector
    def do_plot(self, data: pd.DataFrame, *, label: str, color: str = "k"):
        yaxis = data[self.quantity]
        yerr = data[self.quantity_err]

        if self.quantity_err:
            plt.errorbar(data["BCID"], yaxis, yerr=yerr, fmt="o", label=label, color=color)
        else:
            plt.plot(data["BCID"], yaxis, "o", label=label, color=color)

    def style_plot(self, *, scan_name: str = "", fit: str = "", correction: str = ""):
        title = TitleBuilder()\
                .set_scan_name(scan_name)\
                .set_fit(fit)\
                .set_correction(correction)\
                .set_axis(self.axis_text)\
                .set_info(self.latex)\
                .build()

        plt.title(title)
        plt.xlabel("BCID")
        plt.ylabel(self.latex)

        plt.grid()
        plt.legend()

    def save_plot(self, ouput_dir: Path, file_name: str, *, suffix: str = "", file_ext: str = "png"):
        path = ouput_dir/"bcid"/self.output_folder_name/self.current_detector
        path.mkdir(parents=True, exist_ok=True)

        file_name = f"{self.file_name_prepend}{file_name}{suffix}.{file_ext}"

        plt.savefig(path/file_name)


@dataclass
class CapSigmaXBCIDPlotStrategy(BCIDPlotStrategy):
    latex: str = r"$\Sigma_X$"
    quantity: str = "CapSigma_X"
    quantity_err: str = "CapSigmaErr_X"
    output_folder_name: str = "capsigma"
    plot_per_detector: bool = False

    axis_text: str = "X Scan"
    file_name_prepend: str = "X_"


@dataclass
class CapSigmaYBCIDPlotStrategy(BCIDPlotStrategy):
    latex: str = r"$\Sigma_Y$"
    quantity: str = "CapSigma_Y"
    quantity_err: str = "CapSigmaErr_Y"
    output_folder_name: str = "capsigma"
    plot_per_detector: bool = False

    axis_text: str = "Y Scan"
    file_name_prepend: str = "Y_"


@dataclass
class PeakXBCIDPlotStrategy(BCIDPlotStrategy):
    latex: str = r"$\mathrm{Peak}_X$"
    quantity: str = "peak_X"
    quantity_err: str = "peakErr_X"
    output_folder_name: str = "peak"
    plot_per_detector: bool = True

    axis_text: str = "X Scan"
    file_name_prepend: str = "X_"


@dataclass
class PeakYBCIDPlotStrategy(BCIDPlotStrategy):
    latex: str = r"$\mathrm{Peak}_Y$"
    quantity: str = "peak_Y"
    quantity_err: str = "peakErr_Y"
    output_folder_name: str = "peak"
    plot_per_detector: bool = True

    axis_text: str = "Y Scan"
    file_name_prepend: str = "Y_"


@dataclass
class SigVisBCIDPlotStrategy(BCIDPlotStrategy):
    latex: str = r"$\sigma_{\mathrm{vis}}$"
    quantity: str = "xsec"
    quantity_err: str = "xsecErr"
    output_folder_name: str = "sigvis"
    plot_per_detector: bool = True


@dataclass
class SBILBCIDPlotStrategy(BCIDPlotStrategy):
    latex: str = r"SBIL"
    quantity: str = "SBIL"
    quantity_err: str = "SBILErr"
    output_folder_name: str = "sbil"
    plot_per_detector: bool = False


@dataclass
class RChi2XBCIDPlotStrategy(BCIDPlotStrategy):
    latex: str = r"$\chi_{\mathrm{reduced}_X}^2$"
    quantity: str = "chi2_X"
    output_folder_name: str = "rchi2"
    plot_per_detector: bool = False

    axis_text: str = "X Scan"
    file_name_prepend: str = "X_"

    def do_plot(self, data: pd.DataFrame, *, label: str, color: str = "k"):
        yaxis = data[self.quantity] / data["ndof_X"]
        plt.plot(data["BCID"], yaxis, "o", label=label, color=color)


@dataclass
class RChi2YBCIDPlotStrategy(BCIDPlotStrategy):
    latex: str = r"$\chi_{\mathrm{reduced}_Y}^2$"
    quantity: str = "chi2_Y"
    output_folder_name: str = "rchi2"
    plot_per_detector: bool = False

    axis_text: str = "Y Scan"
    file_name_prepend: str = "Y_"

    def do_plot(self, data: pd.DataFrame, *, label: str, color: str = "k"):
        yaxis = data[self.quantity] / data["ndof_Y"]
        plt.plot(data["BCID"], yaxis, "o", label=label, color=color)
