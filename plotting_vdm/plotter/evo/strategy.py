from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Sequence, Optional, Callable
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from plotting_vdm.plotter.utils import TitleBuilder


def _set_current_detector(method):
    def do_plot_wrapper(self: EvoPlotStrategy, datas: Sequence[pd.DataFrame], *args, **kwargs):
        if self.plot_per_detector:
            self.current_detector = datas[0]["detector"].unique().item()

        return method(self, datas, *args, **kwargs)

    return do_plot_wrapper


@dataclass
class EvoPlotStrategy:
    latex: str
    quantity: str
    quantity_err: str
    plot_per_detector: bool

    xlabel: str = ""
    add_legend: bool = True
    file_name_prepend: str = ""
    output_folder_name: str = ""
    scan_stats: Callable[
        [pd.Series, pd.Series], # Arguments: value, error
        Tuple[float, float] # Return: avg, err
    ] = lambda x, _: (x.mean(), x.std())
    plot_fit: bool = False
    fit_stats: Callable[
        [np.ndarray, np.ndarray], # Arguments: value, error
        Tuple[float, float] # Return: avg, err
    ] = lambda x, _: (x.mean(), x.std())

    def __post_init__(self):
        self.current_detector = ""

    @property
    def plot_per_detector(self) -> bool:
        return self.plot_per_detector

    @_set_current_detector
    def do_plot(self, datas: Sequence[pd.DataFrame], *, label: str, color: str = "k"):
        x_data = np.empty(len(datas))
        y_data = np.empty(len(datas))
        y_err  = np.empty(len(datas))

        for i, data in enumerate(datas):
            avg, err = self.scan_stats(data[self.quantity], data[self.quantity_err])

            x_data[i] = i+1
            y_data[i] = avg
            y_err[i]  = err

        plt.errorbar(x_data, y_data, yerr=y_err, fmt="o", label=label, color=color)

        if self.plot_fit:
            avg, err = self.fit_stats(y_data, y_err)
            rchi2 = np.sum((y_data - avg)**2 / y_err**2) / (len(y_data) - 1)
            plt.axhline(avg, color=color, linestyle="--")
            plt.axhspan(avg - err, avg + err, color=color, alpha=0.3)
            plt.figtext(
                x=0.88,
                y=0.87,
                ha="right",
                va="top",
                fontsize=12,
                s=f"{self.latex} = {avg:.2f} $\pm$ {err:.2f} (stat)\n$\chi^2/ndof$ = {rchi2:.2f}",
                backgroundcolor="white",
            ).set_bbox(dict(color="w", alpha=1))

        plt.xlim(0, len(datas) + 1)

    def style_plot(self, *, fit: str, correction: str, xticks: Optional[List[str]] = None):
        if xticks is not None:
            plt.xticks(range(1, len(xticks) + 1), xticks)

        title = TitleBuilder()\
                .set_info(self.latex)\
                .set_fit(fit)\
                .set_correction(correction)\
                .build()

        plt.title(title)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.latex)

        plt.grid()
        if self.add_legend: plt.legend(loc="best")
        plt.ticklabel_format(useOffset=False, axis="y") # Disable scientific notation

    def save_plot(self, ouput_dir: Path, file_name: str, *, suffix: str = "", file_ext: str = "png"):
        path = ouput_dir/"evolution"/self.output_folder_name/self.current_detector
        path.mkdir(parents=True, exist_ok=True)

        file_name = f"{self.file_name_prepend}{file_name}{suffix}.{file_ext}"

        plt.savefig(path/file_name)


@dataclass
class CapSigmaXEvoPlotStrategy(EvoPlotStrategy):
    latex: str = r"$\Sigma_{X}$"
    quantity: str = "CapSigma_X"
    quantity_err: str = "CapSigmaErr_X"
    plot_per_detector: bool = False
    output_folder_name: str = "capsigma"

    xlabel: str = "Scan number"
    file_name_prepend: str = "X_"


@dataclass
class CapSigmaYEvoPlotStrategy(EvoPlotStrategy):
    latex: str = r"$\Sigma_{Y}$"
    quantity: str = "CapSigma_Y"
    quantity_err: str = "CapSigmaErr_Y"
    plot_per_detector: bool = False
    output_folder_name: str = "capsigma"

    xlabel: str = "Scan number"
    file_name_prepend: str = "Y_"


@dataclass
class SigVisEvoPlotStrategy(EvoPlotStrategy):
    latex: str = r"$\sigma_{\mathrm{vis}}$"
    quantity: str = "xsec"
    quantity_err: str = "xsecErr"
    plot_per_detector: bool = True
    output_folder_name: str = "sigvis"

    xlabel: str = "Scan number"
    add_legend: bool = False
    plot_fit: bool = True
