from typing import List
from dataclasses import dataclass, field


@dataclass
class ResultsConfig:
    path: str
    fits: List[str]
    name: str = ""


@dataclass
class PlotterConfig:
    name: str


@dataclass
class StrategyConfig:
    id: str
    name: str
    quantity: str
    error: str
    kwargs: dict = field(default_factory=dict)


@dataclass
class PlotsConfig:
    plotter_config: PlotterConfig
    strategy_config: StrategyConfig


@dataclass
class PlottingConfig:
    plugins: List[str] = field(default_factory=list)
    results: List[ResultsConfig] = field(default_factory=list)
    plots: List[PlotsConfig] = field(default_factory=list)


def _load_from_dict(plotting_config: dict) -> PlottingConfig:
    plugins = plotting_config.get("plugins", [])

    results_config = [
        ResultsConfig(**result)
        for result in plotting_config["results"]
    ]

    plots_config = [
        PlotsConfig(
            plotter_config=PlotterConfig(**plot["plotter"]),
            strategy_config=StrategyConfig(**plot["strategy"]),
        )
        for plot in plotting_config["plots"]
    ]

    return PlottingConfig(
        plugins=plugins,
        results=results_config,
        plots=plots_config,
    )
