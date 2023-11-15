from pathlib import Path
from typing import Dict, Any

import numpy as np
from scan_results import ScanResults
from title_builder import TitleBuilder
from functions import match_bcids

import matplotlib.pyplot as plt


class PlotStrategy:
    def __init__(self, **kwargs):
        self.context: Dict[str, Any] = {}

        self.xlabel = kwargs.get("xlabel", "BCID")
        self.legend_loc = kwargs.get("legend_loc", "best")
        self.output_dir: Path = kwargs.get("output_dir", Path("."))
        if not isinstance(self.output_dir, Path):
            self.output_dir = Path(self.output_dir)
        self.output_dir = self.output_dir/"plots"
        self.fmt = kwargs.get("fmt", "o")
        self.legend_fontsize = kwargs.get("legend_fontsize", 12)
        self.colors = kwargs.get("colors", ["k", "r", "b", "g", "m", "c", "y"])
        self.markersize = kwargs.get("markersize", 5)

    def on_correction_loop_entry(self, results: ScanResults, fit: str, correction: str) -> bool:
        """
        on_correction_loop_entry
        """
        return False

    def on_detector_loop(self, i, results: ScanResults, fit: str, correction: str, detector: str):
        """
        on_detector_loop
        """

    def on_correction_loop_exit(self, results: ScanResults, fit: str, correction: str):
        """
        on_correction_loop_exit
        """


class NormalPlotStrategy(PlotStrategy):
    def __init__(self, quantity: str, error: str, quantity_latex: str = "", **kwargs):
        super().__init__(**kwargs)
        self.quantity = quantity
        self.error = error
        self.quantity_latex = quantity_latex if quantity_latex else quantity

        self.output_dir = self.output_dir/"normal"

    def on_correction_loop_entry(self, results: ScanResults, fit, correction) -> bool:
        plt.clf()
        plt.style.use("classic")
        plt.rcParams["legend.numpoints"] = 1

        return False

    def on_detector_loop(self, i, results: ScanResults, fit, correction, detector):
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

    def on_correction_loop_exit(self, results: ScanResults, fit, correction):
        title = TitleBuilder() \
                .set_fit(fit) \
                .set_correction(correction) \
                .set_info(results.name).build()

        plt.grid()
        plt.title(title)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.quantity_latex)
        plt.legend(loc=self.legend_loc, fontsize=self.legend_fontsize)
        plt.ticklabel_format(useOffset=False, axis="y")  # Prevent plt from adding offset to y axis

        path = self.output_dir/results.id_str/self.quantity/fit
        path.mkdir(parents=True, exist_ok=True)

        file = f"{correction}.png"
        plt.savefig(path/file)


class NormalSeparatePlotStrategy(PlotStrategy):
    def __init__(self, quantity: str, error: str, quantity_latex: str = "", **kwargs):
        super().__init__()
        self.quantity = quantity
        self.error = error
        self.quantity_latex = quantity_latex if quantity_latex else quantity

        self.output_dir = self.output_dir/"normal"
        self.color = kwargs.get("color", "b")

    def on_detector_loop(self, i, results: ScanResults, fit, correction, detector):
        plt.clf()
        plt.style.use("classic")
        plt.rcParams["legend.numpoints"] = 1

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


class RatioPlotStrategy(PlotStrategy):
    def __init__(self, reference_detector:str, quantity: str, error: str, quantity_latex: str = "", **kwargs):
        super().__init__()
        self.reference_detector = reference_detector
        self.quantity = quantity
        self.error = error
        self.quantity_latex = quantity_latex if quantity_latex else quantity

        self.output_dir = self.output_dir/"ratio"

    def on_correction_loop_entry(self, results: ScanResults, fit: str, correction: str) -> bool:
        plt.clf()
        plt.style.use("classic")
        plt.rcParams["legend.numpoints"] = 1

        return False

    def on_detector_loop(self, i, results: ScanResults, fit: str, correction: str, detector: str):
        if detector == self.reference_detector:
            return

        data = results.filter_results_by(
            fit, correction, detector, quality="good"
        ).set_index("BCID")
        ref = results.filter_results_by(
            fit, correction, self.reference_detector, quality="good"
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
        )

    def on_correction_loop_exit(self, results: ScanResults, fit, correction):
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


class CorrPlotStrategy(PlotStrategy):
    def __init__(self, base_correction:str, quantity: str, error: str, quantity_latex: str = "", **kwargs):
            super().__init__()
            self.base_correction = base_correction
            self.quantity = quantity
            self.error = error
            self.quantity_latex = quantity_latex if quantity_latex else quantity

            self.output_dir = self.output_dir/"corr"

    def on_correction_loop_entry(self, results: ScanResults, fit: str, correction: str) -> bool:
        if correction == "no_corr":
            return True

        plt.clf()
        plt.style.use("classic")
        plt.rcParams["legend.numpoints"] = 1

        self.context["reference"] = self.get_reference_correction(correction, results.corrections)

        return False

    def on_detector_loop(self, i, results: ScanResults, fit: str, correction: str, detector: str):
        data = results.filter_results_by(
            fit, correction, detector, quality="good"
        ).set_index("BCID")
        ref = results.filter_results_by(
            fit, self.context["reference"], detector, quality="good"
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

    def on_correction_loop_exit(self, results: ScanResults, fit, correction):
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


class ScanPlotter:
    def __init__(self, plot_strategy: PlotStrategy = None):
        self.plot_strategy = plot_strategy

    def __call__(self, results: ScanResults):
        self.plot(results)

    def plot(self, results: ScanResults):
        if self.plot_strategy is None:
            raise NotImplementedError("No plot strategy set")

        for fit in results.fits:

            for correction in results.corrections:
                skip_correction = self.plot_strategy.on_correction_loop_entry(results, fit, correction)

                if skip_correction:
                    continue

                for i, detector in enumerate(results.detectors):
                    self.plot_strategy.on_detector_loop(i, results, fit, correction, detector)

                self.plot_strategy.on_correction_loop_exit(results, fit, correction)


if __name__ == "__main__":
    scan = ScanResults(Path("analysed_data/8381_11Nov22_114759_11Nov22_121408"), fits=["SG", "DG"])
    plotter = ScanPlotter()

    strategy = NormalPlotStrategy(
        quantity="CapSigma_X",
        error="CapSigmaErr_X",
        quantity_latex=r"$\Sigma_X$",
    )
    plotter.plot_strategy = strategy
    plotter(scan)

    strategy = NormalPlotStrategy(
        quantity="CapSigma_Y",
        error="CapSigmaErr_Y",
        quantity_latex=r"$\Sigma_Y$",
    )
    plotter.plot_strategy = strategy
    plotter(scan)

    # strategy = NormalSeparatePlotStrategy(
    #     quantity="CapSigma_X",
    #     error="CapSigmaErr_X",
    #     quantity_latex=r"$\Sigma_X$",
    # )
    # plotter.plot_strategy = strategy
    # plotter(scan)

    # strategy = NormalSeparatePlotStrategy(
    #     quantity="CapSigma_Y",
    #     error="CapSigmaErr_Y",
    #     quantity_latex=r"$\Sigma_Y$",
    # )
    # plotter.plot_strategy = strategy
    # plotter(scan)

    strategy = NormalPlotStrategy(
        quantity="peak_X",
        error="peakErr_X",
        quantity_latex=r"$\mathrm{Peak}_X$",
    )
    plotter.plot_strategy = strategy
    plotter(scan)

    strategy = NormalPlotStrategy(
        quantity="peak_Y",
        error="peakErr_Y",
        quantity_latex=r"$\mathrm{Peak}_Y$",
    )
    plotter.plot_strategy = strategy
    plotter(scan)

    # strategy = NormalSeparatePlotStrategy(
    #     quantity="peak_X",
    #     error="peakErr_X",
    #     quantity_latex=r"$\mathrm{Peak}_X$",
    # )
    # plotter.plot_strategy = strategy
    # plotter(scan)

    # strategy = NormalSeparatePlotStrategy(
    #     quantity="peak_Y",
    #     error="peakErr_Y",
    #     quantity_latex=r"$\mathrm{Peak}_Y$",
    # )
    # plotter.plot_strategy = strategy
    # plotter(scan)

    strategy = NormalPlotStrategy(
        quantity="xsec",
        error="xsecErr",
        quantity_latex=r"$\sigma_{\mathrm{vis}}$",
    )
    plotter.plot_strategy = strategy
    plotter(scan)

    # strategy = NormalSeparatePlotStrategy(
    #     quantity="xsec",
    #     error="xsecErr",
    #     quantity_latex=r"$\sigma_{\mathrm{vis}}$",
    # )
    # plotter.plot_strategy = strategy
    # plotter(scan)

    # strategy = RatioPlotStrategy(
    #     reference_detector="HFOC",
    #     quantity="CapSigma_X",
    #     error="CapSigmaErr_X",
    #     quantity_latex=r"$\Sigma_X$",
    # )
    # plotter.plot_strategy = strategy
    # plotter(scan)

    # strategy = RatioPlotStrategy(
    #     reference_detector="HFOC",
    #     quantity="CapSigma_Y",
    #     error="CapSigmaErr_Y",
    #     quantity_latex=r"$\Sigma_Y$",
    # )
    # plotter.plot_strategy = strategy
    # plotter(scan)

    # strategy = CorrPlotStrategy(
    #     base_correction="Background",
    #     quantity="CapSigma_X",
    #     error="CapSigmaErr_X",
    #     quantity_latex=r"$\Sigma_X$",
    # )
    # plotter.plot_strategy = strategy
    # plotter(scan)

    # strategy = CorrPlotStrategy(
    #     base_correction="Background",
    #     quantity="CapSigma_Y",
    #     error="CapSigmaErr_Y",
    #     quantity_latex=r"$\Sigma_Y$",
    # )
    # plotter.plot_strategy = strategy
    # plotter(scan)

    # strategy = CorrPlotStrategy(
    #     base_correction="Background",
    #     quantity="peak_X",
    #     error="peakErr_X",
    #     quantity_latex=r"$\Sigma_X$",
    # )
    # plotter.plot_strategy = strategy
    # plotter(scan)

    # strategy = CorrPlotStrategy(
    #     base_correction="Background",
    #     quantity="peak_Y",
    #     error="peakErr_Y",
    #     quantity_latex=r"$\Sigma_Y$",
    # )
    # plotter.plot_strategy = strategy
    # plotter(scan)

    # strategy = CorrPlotStrategy(
    #     base_correction="Background",
    #     quantity="xsec",
    #     error="xsecErr",
    #     quantity_latex=r"$\sigma_{\mathrm{vis}}$",
    # )
    # plotter.plot_strategy = strategy
    # plotter(scan)
