import matplotlib.pyplot as plt

from plotting_vdm.scan_results import ScanResults
from plotting_vdm._typing import OneOrMany
from plotting_vdm.utils.title_builder import TitleBuilder
from .base import PlotStrategy


class NormalPlotStrategy(PlotStrategy):
    def __init__(self, quantity: str, error: str, quantity_latex: str = "", **kwargs):
        super().__init__(**kwargs)
        self.quantity = quantity
        self.error = error
        self.quantity_latex = quantity_latex if quantity_latex else quantity

        self.output_dir = self.output_dir/"normal"
        self.xlabel = kwargs.get("xlabel", "BCID")

    def on_correction_loop_entry(self, results: OneOrMany[ScanResults], fit, correction) -> bool:
        plt.clf()

        return False

    def on_detector_loop(self, i, results: OneOrMany[ScanResults], fit, correction, detector):
        data = results.filter_results_by(fit, correction, detector, quality="good")

        plt.errorbar(
            data["BCID"],
            data[self.quantity],
            yerr=data[self.error],
            label=detector,
            fmt=self.fmt,
            color=self.colors[i],
            markersize=self.markersize,
        )

    def on_correction_loop_exit(self, results: OneOrMany[ScanResults], fit, correction):
        title = TitleBuilder() \
                .set_fit(fit) \
                .set_correction(correction) \
                .set_info(results.name).build()

        plt.grid()
        plt.title(title)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.quantity_latex)
        plt.legend(loc=self.legend_loc, fontsize=self.legend_fontsize)
        plt.ticklabel_format(useOffset=False, axis="y")

        path = self.output_dir/results.id_str/self.quantity/fit
        path.mkdir(parents=True, exist_ok=True)

        file = f"{correction}.png"
        plt.savefig(path/file)


class NormalSeparatePlotStrategy(PlotStrategy):
    def __init__(self, quantity: str, error: str, quantity_latex: str = "", **kwargs):
        super().__init__(**kwargs)
        self.quantity = quantity
        self.error = error
        self.quantity_latex = quantity_latex if quantity_latex else quantity

        self.output_dir = self.output_dir/"normal"
        self.color = kwargs.get("color", "b")
        self.xlabel = kwargs.get("xlabel", "BCID")

    def on_detector_loop(self, i, results: OneOrMany[ScanResults], fit, correction, detector):
        plt.clf()

        data = results.filter_results_by(fit, correction, detector, quality="good")

        plt.errorbar(
            data["BCID"],
            data[self.quantity],
            yerr=data[self.error],
            fmt=self.fmt,
            color=self.color,
            markersize=self.markersize,
        )

        title = TitleBuilder() \
                .set_fit(fit) \
                .set_detector(detector) \
                .set_correction(correction) \
                .set_info(results.name).build()

        plt.grid()
        plt.title(title)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.quantity_latex)
        plt.ticklabel_format(useOffset=False, axis="y")  # Prevent plt from adding offset to y axis

        path = self.output_dir/results.id_str/self.quantity/"separete"/fit/detector
        path.mkdir(parents=True, exist_ok=True)

        file = f"{correction}.png"
        plt.savefig(path/file)
