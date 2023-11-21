from pathlib import Path

from plotting_vdm.plotter import VdMPlotter
from plotting_vdm.scan_results import ScanResults
from plotting_vdm.common.strategies import corr, normal, ratio, evo


if __name__ == "__main__":
    # scan = ScanResults(Path("analysed_data/8381_11Nov22_114759_11Nov22_121408"), fits=["SG", "DG"])
    # plotter = VdMPlotter()

    # strategy = normal.NormalPlotStrategy(
    #     quantity="CapSigma_X",
    #     error="CapSigmaErr_X",
    #     quantity_latex=r"$\Sigma_X$",
    # )
    # plotter.plot_strategy = strategy
    # plotter(scan)

    # strategy = normal.NormalPlotStrategy(
    #     quantity="CapSigma_Y",
    #     error="CapSigmaErr_Y",
    #     quantity_latex=r"$\Sigma_Y$",
    # )
    # plotter.plot_strategy = strategy
    # plotter(scan)

    # strategy = normal.NormalSeparatePlotStrategy(
    #     quantity="CapSigma_X",
    #     error="CapSigmaErr_X",
    #     quantity_latex=r"$\Sigma_X$",
    # )
    # plotter.plot_strategy = strategy
    # plotter(scan)

    # strategy = normal.NormalSeparatePlotStrategy(
    #     quantity="CapSigma_Y",
    #     error="CapSigmaErr_Y",
    #     quantity_latex=r"$\Sigma_Y$",
    # )
    # plotter.plot_strategy = strategy
    # plotter(scan)

    # strategy = normal.NormalPlotStrategy(
    #     quantity="peak_X",
    #     error="peakErr_X",
    #     quantity_latex=r"$\mathrm{Peak}_X$",
    # )
    # plotter.plot_strategy = strategy
    # plotter(scan)

    # strategy = normal.NormalPlotStrategy(
    #     quantity="peak_Y",
    #     error="peakErr_Y",
    #     quantity_latex=r"$\mathrm{Peak}_Y$",
    # )
    # plotter.plot_strategy = strategy
    # plotter(scan)

    # strategy = normal.NormalSeparatePlotStrategy(
    #     quantity="peak_X",
    #     error="peakErr_X",
    #     quantity_latex=r"$\mathrm{Peak}_X$",
    # )
    # plotter.plot_strategy = strategy
    # plotter(scan)

    # strategy = normal.NormalSeparatePlotStrategy(
    #     quantity="peak_Y",
    #     error="peakErr_Y",
    #     quantity_latex=r"$\mathrm{Peak}_Y$",
    # )
    # plotter.plot_strategy = strategy
    # plotter(scan)

    # strategy = normal.NormalPlotStrategy(
    #     quantity="xsec",
    #     error="xsecErr",
    #     quantity_latex=r"$\sigma_{\mathrm{vis}}$",
    # )
    # plotter.plot_strategy = strategy
    # plotter(scan)

    # strategy = normal.NormalSeparatePlotStrategy(
    #     quantity="xsec",
    #     error="xsecErr",
    #     quantity_latex=r"$\sigma_{\mathrm{vis}}$",
    # )
    # plotter.plot_strategy = strategy
    # plotter(scan)

    # strategy = ratio.RatioPlotStrategy(
    #     reference_detector="HFOC",
    #     quantity="CapSigma_X",
    #     error="CapSigmaErr_X",
    #     quantity_latex=r"$\Sigma_X$",
    # )
    # plotter.plot_strategy = strategy
    # plotter(scan)

    # strategy = ratio.RatioPlotStrategy(
    #     reference_detector="HFOC",
    #     quantity="CapSigma_Y",
    #     error="CapSigmaErr_Y",
    #     quantity_latex=r"$\Sigma_Y$",
    # )
    # plotter.plot_strategy = strategy
    # plotter(scan)

    # strategy = corr.CorrPlotStrategy(
    #     base_correction="Background",
    #     quantity="CapSigma_X",
    #     error="CapSigmaErr_X",
    #     quantity_latex=r"$\Sigma_X$",
    # )
    # plotter.plot_strategy = strategy
    # plotter(scan)

    # strategy = corr.CorrPlotStrategy(
    #     base_correction="Background",
    #     quantity="CapSigma_Y",
    #     error="CapSigmaErr_Y",
    #     quantity_latex=r"$\Sigma_Y$",
    # )
    # plotter.plot_strategy = strategy
    # plotter(scan)

    # strategy = corr.CorrPlotStrategy(
    #     base_correction="Background",
    #     quantity="peak_X",
    #     error="peakErr_X",
    #     quantity_latex=r"$\Sigma_X$",
    # )
    # plotter.plot_strategy = strategy
    # plotter(scan)

    # strategy = corr.CorrPlotStrategy(
    #     base_correction="Background",
    #     quantity="peak_Y",
    #     error="peakErr_Y",
    #     quantity_latex=r"$\Sigma_Y$",
    # )
    # plotter.plot_strategy = strategy
    # plotter(scan)

    # strategy = corr.CorrPlotStrategy(
    #     base_correction="Background",
    #     quantity="xsec",
    #     error="xsecErr",
    #     quantity_latex=r"$\sigma_{\mathrm{vis}}$",
    # )
    # plotter.plot_strategy = strategy
    # plotter(scan)

    fill_8999 = {
        # "8999_28Jun23_222504_28Jun23_223127": "emit1",
        "8999_28Jun23_230143_28Jun23_232943": "VdM1",
        # "8999_28Jun23_235337_29Jun23_001656": "ds1",
        "8999_29Jun23_004658_29Jun23_011220": "BI1",
        "8999_29Jun23_013851_29Jun23_020425": "BI2",
        "8999_29Jun23_023227_29Jun23_025502": "VdM2",
        "8999_29Jun23_073830_29Jun23_080352": "VdM3",
        # "8999_29Jun23_083200_29Jun23_085852": "os1",
        "8999_29Jun23_092415_29Jun23_094738": "VdM4",
        # "8999_29Jun23_101314_29Jun23_103550": "ds2",
        "8999_29Jun23_110004_29Jun23_112226": "VdM5",
        # "8999_29Jun23_114555_29Jun23_115221": "emit2",
        "8999_29Jun23_123257_29Jun23_125514": "VdM6",
        # "8999_29Jun23_211111_29Jun23_211737": "emit3",
    }

    results_path = Path(input("Output path (example: /eos/user/f/flpereir/www/8999_output): "))
    if not results_path.exists():
        raise ValueError(f"Path {results_path} does not exist")
    res_path = results_path/"analysed_data"
    all_scans = [ScanResults(path, fits=["DG"], name=fill_8999[path.stem]) for path in res_path.glob("8999*") if path.stem in fill_8999]
    plotter = VdMPlotter()
    all_scans.sort(key=lambda s: s.start)

    strategy = evo.EvoSeparatePlotStrategy(
        quantity="xsec",
        error="xsecErr",
        quantity_latex=r"$\sigma_{\mathrm{vis}}$",
        fmt="s",
        markersize=8,
        elinewidth=0.5,
        output_dir=results_path,
    )
    plotter.plot_strategy = strategy
    plotter(all_scans)
    print(f"Plots saved in {results_path/'plots'}")

    # output = Path("/eos/user/f/flpereir/www/8999_output_with_gs")
    # res_path = Path("/eos/user/f/flpereir/www/8999_output_with_gs/analysed_data")
    # all_scans = [ScanResults(path, fits=["DG"], name=fill_8999[path.stem]) for path in res_path.glob("8999*") if path.stem in fill_8999]
    # plotter = VdMPlotter()
    # all_scans.sort(key=lambda s: s.start)

    # strategy = evo.EvoSeparatePlotStrategy(
    #     quantity="xsec",
    #     error="xsecErr",
    #     quantity_latex=r"$\sigma_{\mathrm{vis}}$",
    #     fmt="s",
    #     markersize=8,
    #     elinewidth=0.5,
    #     output_dir=output,
    # )
    # plotter.plot_strategy = strategy
    # plotter(all_scans)

    # strategy = evo.EvoPlotStrategy(
    #     quantity="CapSigma_X",
    #     error="CapSigmaErr_X",
    #     quantity_latex=r"$\Sigma_X$",
    # )
    # plotter.plot_strategy = strategy
    # plotter(all_scans)

    # strategy = evo.EvoPlotStrategy(
    #     quantity="CapSigma_Y",
    #     error="CapSigmaErr_Y",
    #     quantity_latex=r"$\Sigma_Y$",
    # )
    # plotter.plot_strategy = strategy
    # plotter(all_scans)
