from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass, field

from scan_results import ScanResults
from title_builder import TitleBuilder

import matplotlib.pyplot as plt


@dataclass
class PlotStrategy:
    context: Dict[str, Any] = field(default_factory=dict)

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
        super().__init__()
        self.quantity = quantity
        self.error = error
        self.quantity_latex = quantity_latex if quantity_latex else quantity

        self.xlabel = kwargs.get("xlabel", "BCID")
        self.legend_loc = kwargs.get("legend_loc", "best")
        self.output_dir: Path = kwargs.get("output_dir", Path("."))
        if not isinstance(self.output_dir, Path):
            self.output_dir = Path(self.output_dir)
        self.output_dir = self.output_dir/"plots"/"normal"

    def on_correction_loop_entry(self, results: ScanResults, fit, correction) -> bool:
        plt.clf()
        plt.style.use("classic")
        plt.rcParams["legend.numpoints"] = 1

        return False

    def on_detector_loop(self, i, results: ScanResults, fit, correction, detector):
        data = results.results[fit].query(f"correction == '{correction}' and detector == '{detector}'")

        fmt = self.context.get("fmt", "o")
        colors = self.context.get("colors", ["k", "r", "g", "b", "m", "c", "y"])

        plt.errorbar(
            data["BCID"],
            data[self.quantity],
            yerr=data[self.error],
            label=detector,
            fmt=fmt,
            color=colors[i],
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
        plt.legend(loc=self.legend_loc)
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

        self.xlabel = kwargs.get("xlabel", "BCID")
        self.output_dir: Path = kwargs.get("output_dir", Path("."))
        if not isinstance(self.output_dir, Path):
            self.output_dir = Path(self.output_dir)
        self.output_dir = self.output_dir/"plots"/"normal"
        self.fmt = kwargs.get("fmt", "o")
        self.color = kwargs.get("color", "b")

    def on_detector_loop(self, i, results: ScanResults, fit, correction, detector):
        plt.clf()
        plt.style.use("classic")
        plt.rcParams["legend.numpoints"] = 1

        data = results.results[fit].query(f"correction == '{correction}' and detector == '{detector}'")

        plt.errorbar(
            data["BCID"],
            data[self.quantity],
            yerr=data[self.error],
            fmt=self.fmt,
            color=self.color,
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
    strategyX = NormalPlotStrategy(
        quantity="CapSigma_X",
        error="CapSigmaErr_X",
        quantity_latex=r"$\Sigma_X$",
    )
    strategyY = NormalPlotStrategy(
        quantity="CapSigma_Y",
        error="CapSigmaErr_Y",
        quantity_latex=r"$\Sigma_Y$",
    )
    strategyPX = NormalSeparatePlotStrategy(
        quantity="peak_X",
        error="peakErr_X",
        quantity_latex=r"$\mathrm{Peak}_X$",
    )
    strategyPY = NormalSeparatePlotStrategy(
        quantity="peak_Y",
        error="peakErr_Y",
        quantity_latex=r"$\mathrm{Peak}_Y$",
    )
    strategySV = NormalSeparatePlotStrategy(
        quantity="xsec",
        error="xsecErr",
        quantity_latex=r"$\sigma_\mathrm{vis}$",
    )
    plotterY = ScanPlotter(strategyY)
    plotterY(scan)
    plotterX = ScanPlotter(strategyX)
    plotterX(scan)
    plotterPY = ScanPlotter(strategyPY)
    plotterPY(scan)
    plotterPX = ScanPlotter(strategyPX)
    plotterPX(scan)
    plotterSV = ScanPlotter(strategySV)
    plotterSV(scan)
