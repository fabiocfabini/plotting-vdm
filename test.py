from pathlib import Path

from plotting_vdm.scan_results import ScanResults
from plotting_vdm.scan.plotter import ScanPlotter
from plotting_vdm.scan.strategies import corr, normal, ratio


if __name__ == "__main__":
    scan = ScanResults(Path("analysed_data/8381_11Nov22_114759_11Nov22_121408"), fits=["SG", "DG"])
    plotter = ScanPlotter()

    strategy = normal.NormalPlotStrategy(
        quantity="CapSigma_X",
        error="CapSigmaErr_X",
        quantity_latex=r"$\Sigma_X$",
    )
    plotter.plot_strategy = strategy
    plotter(scan)

    strategy = normal.NormalPlotStrategy(
        quantity="CapSigma_Y",
        error="CapSigmaErr_Y",
        quantity_latex=r"$\Sigma_Y$",
    )
    plotter.plot_strategy = strategy
    plotter(scan)

    strategy = normal.NormalSeparatePlotStrategy(
        quantity="CapSigma_X",
        error="CapSigmaErr_X",
        quantity_latex=r"$\Sigma_X$",
    )
    plotter.plot_strategy = strategy
    plotter(scan)

    strategy = normal.NormalSeparatePlotStrategy(
        quantity="CapSigma_Y",
        error="CapSigmaErr_Y",
        quantity_latex=r"$\Sigma_Y$",
    )
    plotter.plot_strategy = strategy
    plotter(scan)

    strategy = normal.NormalPlotStrategy(
        quantity="peak_X",
        error="peakErr_X",
        quantity_latex=r"$\mathrm{Peak}_X$",
    )
    plotter.plot_strategy = strategy
    plotter(scan)

    strategy = normal.NormalPlotStrategy(
        quantity="peak_Y",
        error="peakErr_Y",
        quantity_latex=r"$\mathrm{Peak}_Y$",
    )
    plotter.plot_strategy = strategy
    plotter(scan)

    strategy = normal.NormalSeparatePlotStrategy(
        quantity="peak_X",
        error="peakErr_X",
        quantity_latex=r"$\mathrm{Peak}_X$",
    )
    plotter.plot_strategy = strategy
    plotter(scan)

    strategy = normal.NormalSeparatePlotStrategy(
        quantity="peak_Y",
        error="peakErr_Y",
        quantity_latex=r"$\mathrm{Peak}_Y$",
    )
    plotter.plot_strategy = strategy
    plotter(scan)

    strategy = normal.NormalPlotStrategy(
        quantity="xsec",
        error="xsecErr",
        quantity_latex=r"$\sigma_{\mathrm{vis}}$",
    )
    plotter.plot_strategy = strategy
    plotter(scan)

    strategy = normal.NormalSeparatePlotStrategy(
        quantity="xsec",
        error="xsecErr",
        quantity_latex=r"$\sigma_{\mathrm{vis}}$",
    )
    plotter.plot_strategy = strategy
    plotter(scan)

    strategy = ratio.RatioPlotStrategy(
        reference_detector="HFOC",
        quantity="CapSigma_X",
        error="CapSigmaErr_X",
        quantity_latex=r"$\Sigma_X$",
    )
    plotter.plot_strategy = strategy
    plotter(scan)

    strategy = ratio.RatioPlotStrategy(
        reference_detector="HFOC",
        quantity="CapSigma_Y",
        error="CapSigmaErr_Y",
        quantity_latex=r"$\Sigma_Y$",
    )
    plotter.plot_strategy = strategy
    plotter(scan)

    strategy = corr.CorrPlotStrategy(
        base_correction="Background",
        quantity="CapSigma_X",
        error="CapSigmaErr_X",
        quantity_latex=r"$\Sigma_X$",
    )
    plotter.plot_strategy = strategy
    plotter(scan)

    strategy = corr.CorrPlotStrategy(
        base_correction="Background",
        quantity="CapSigma_Y",
        error="CapSigmaErr_Y",
        quantity_latex=r"$\Sigma_Y$",
    )
    plotter.plot_strategy = strategy
    plotter(scan)

    strategy = corr.CorrPlotStrategy(
        base_correction="Background",
        quantity="peak_X",
        error="peakErr_X",
        quantity_latex=r"$\Sigma_X$",
    )
    plotter.plot_strategy = strategy
    plotter(scan)

    strategy = corr.CorrPlotStrategy(
        base_correction="Background",
        quantity="peak_Y",
        error="peakErr_Y",
        quantity_latex=r"$\Sigma_Y$",
    )
    plotter.plot_strategy = strategy
    plotter(scan)

    strategy = corr.CorrPlotStrategy(
        base_correction="Background",
        quantity="xsec",
        error="xsecErr",
        quantity_latex=r"$\sigma_{\mathrm{vis}}$",
    )
    plotter.plot_strategy = strategy
    plotter(scan)