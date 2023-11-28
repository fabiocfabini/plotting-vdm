from typing import Dict
from pathlib import Path

from types import ModuleType

import json
import yaml
import importlib.util

from vdm_tools.io import ScanResults
from .._plugins import PluginConfig
from .plotters import VdMPlotter, PerDetectorPlotter
from .strategy import StrategyPluginCore
from ._config import PlottingConfig, StrategyConfig, PlotterConfig, _load_from_dict


class PlottingEngine:
    def __init__(self, plotting_config_path: str, plotting_plugins_path: str):
        self.registered_modules: Dict[str, StrategyPluginCore] = {}
        self.plotting_plugins_path = Path(plotting_plugins_path)

        self.plotting_config = self._load_plotting_config(plotting_config_path)

    def start(self):
        """Start the plotting engine."""
        self.load_plugins()
        self.show_plugins()

        all_results = [ScanResults(**vars(kwargs)) for kwargs in self.plotting_config.results]
        for plot in self.plotting_config.plots:
            strategy = self._get_strategy(plot.strategy_config)
            plotter = self._get_plotter(plot.plotter_config, strategy)

            plotter(all_results)

    def load_plugins(self, reload: bool = True):
        """Load the plugins specified in the plotting config.

        Parameters
        ----------
        reload : bool
            Reload the plugins if they have already been loaded.
        """
        if reload:
            self._reload_plugins()

        for plugin in self.plotting_config.plugins:
            module = self._load_plugin(plugin)
            self._check_plugin(module)

    def show_plugins(self):
        """Print the loaded plugins."""
        print("Loaded plugins:")
        for plugin in self.registered_modules:
            print(f" - {plugin}")

    def _get_plotter(self, plotter_config: PlotterConfig, strategy: StrategyPluginCore) -> VdMPlotter:
        if plotter_config.name == "PerDetectorPlotter":
            plotter = PerDetectorPlotter(plot_strategy=strategy)
        elif plotter_config.name == "VdMPlotter":
            plotter = VdMPlotter(plot_strategy=strategy)
        else:
            raise ValueError(f"Plotter {plotter_config.name} not found.")

        return plotter

    def _get_strategy(self, strategy_config: StrategyConfig) -> StrategyPluginCore:
        try:
            strategy = self.registered_modules[strategy_config.name]
        except KeyError as exc:
            raise KeyError(f"Strategy {strategy_config.name} not found. Did you load the plugin?") from exc

        return strategy(
            id=strategy_config.id,
            quantity=strategy_config.quantity,
            error=strategy_config.error,
            **strategy_config.kwargs,
        )

    def _check_plugin(self, current_module: ModuleType):
        """Check the plugin was successfully loaded.
        
        Parameters
        ----------
        module : ModuleType
            The module to check.
        """
        if len(StrategyPluginCore.registered_strategies) > 0:
            class_name, class_binding = list(StrategyPluginCore.registered_strategies.items())[-1]
            latest_module_name = class_binding.__module__
            current_module_name = current_module.__name__
            if not latest_module_name == current_module_name:
                raise RuntimeError(f"Plugin {current_module_name} was not loaded correctly.")
            else:
                self.registered_modules[class_name] = class_binding
                StrategyPluginCore.registered_strategies.clear()
        else:
            raise RuntimeError(f"Plugin {current_module_name} was not loaded correctly.")

    def _load_plugin(self, plugin: str) -> ModuleType:
        # Check that the plugin exists
        plugin_path = self.plotting_plugins_path / plugin
        if not plugin_path.exists():
            raise FileNotFoundError(f"Plugin {plugin} not found in {self.plotting_plugins_path}.")

        # Check that the plugin has a plugin.yaml file
        plugin_config_path = plugin_path / "plugin.yaml"
        if not plugin_config_path.exists():
            raise FileNotFoundError(f"Plugin {plugin} does not have a plugin.yaml file.")

        plugin_config = self._load_plugin_config(str(plugin_config_path))

        # Check that the runtime file exists
        plugin_main_path = plugin_path / plugin_config.runtime
        if not plugin_main_path.exists():
            raise FileNotFoundError(f"Plugin {plugin} does not have a runtime file {plugin_config.runtime}.")

        # Convert the path to a module name
        module_name = str(plugin_main_path).replace('/', '.')[:-3]

        # Load the module
        spec = importlib.util.spec_from_file_location(module_name, plugin_main_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        return module

    def _load_plotting_config(self, plotting_config_path: str) -> PlottingConfig:
        with open(plotting_config_path, "r") as f:
            plotting_config = json.load(f)

        return _load_from_dict(plotting_config)

    def _load_plugin_config(self, plugin_config_path: str) -> PluginConfig:
        with open(plugin_config_path, "r") as f:
            plugin_config = yaml.safe_load(f)

        return PluginConfig(**plugin_config)

    def _reload_plugins(self):
        self.registered_modules.clear()
