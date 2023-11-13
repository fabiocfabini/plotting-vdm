from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt

from plotting_vdm.scan_results import ScanResults
from plotting_vdm.plotter.config import PlotterCongig, EvoPlotterConfig
from plotting_vdm.plotter.scan.ratio import *
from plotting_vdm.plotter.scan.normal import *
from plotting_vdm.plotter.scan.corr import *
from plotting_vdm.plotter.evo import *


matplotlib.style.use("classic")
plt.rcParams["legend.numpoints"] = 1

path = Path("/home/fabiocfabini/Desktop/CS/plotting-vdm/analysed_data/").glob("8381*")

fits=["SG", "DG"]
names = ["vdM1", "BI1", "BI2", "vdM2", "vdM3", "vdM4"]
results = [ScanResults(path, fits=fits, name=name) for name, path in zip(names, path)]
results.sort(key=lambda scan: scan.start)


config = PlotterCongig(Path("plots_final"))

bcid_plotter = NormalPlotter(config)
bcid_strategies: list[NormalPlotStrategy] = [
    CapSigmaXNormalPlotStrategy(),
    CapSigmaYNormalPlotStrategy(),
    PeakXNormalPlotStrategy(),
    PeakYNormalPlotStrategy(),
    SigVisNormalPlotStrategy(),
    SBILNormalPlotStrategy(),
]
for bcid_strategy in bcid_strategies:
    bcid_plotter.plot_strategy = bcid_strategy

    bcid_plotter.plot_many(results)

ratio_plotter = RatioPlotter("HFOC", config)
ratio_strategies: list[RatioPlotStrategy] = [
    CapSigmaXRatioPlotStrategy(),
    CapSigmaYRatioPlotStrategy(),
]
for ratio_strategy in ratio_strategies:
    ratio_plotter.plot_strategy = ratio_strategy

    ratio_plotter.plot_many(results)

corr_plotter = CorrPlotter("Background", config)
corr_strategies: list[CorrPlotStrategy] = [
    CapSigmaXCorrPlotStrategy(),
    CapSigmaYCorrPlotStrategy(),
    PeakXCorrPlotStrategy(),
    PeakYCorrPlotStrategy(),
    SigVisCorrPlotStrategy(),
]
for corr_strategy in corr_strategies:
    corr_plotter.plot_strategy = corr_strategy

    corr_plotter.plot_many(results)

evo_config = EvoPlotterConfig(Path("plots_final"), xticks=names)
evo_strategies: list[EvoPlotStrategy] = [
    CapSigmaXEvoPlotStrategy(),
    CapSigmaYEvoPlotStrategy(),
    SigVisEvoPlotStrategy(),
]
evo_plotter = EvoPlotter(evo_config)

for evo_strategy in evo_strategies:
    evo_plotter.plot_strategy = evo_strategy

    if isinstance(evo_strategy, SigVisEvoPlotStrategy):
        evo_config.colors = ["r"] * len(names)

    evo_plotter(results)
