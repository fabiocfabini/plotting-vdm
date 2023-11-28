import argparse

import matplotlib.pyplot as plt

from vdm_tools.plotting.engine import PlottingEngine

plt.style.use("classic")
plt.rcParams["legend.numpoints"] = 1

def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Entry point for the vdm plotting engine.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "plotting_config",
        type=str,
        help="Path to the plotting config.",
    )
    parser.add_argument(
        "plotting_plugins",
        type=str,
        help="Path to the plotting plugins.",
    )

    return parser


def main() -> PlottingEngine:
    parser = create_parser().parse_args()

    engine = PlottingEngine(
        plotting_config_path=parser.plotting_config,
        plotting_plugins_path=parser.plotting_plugins
    )
    engine.start()

    return engine


if __name__ == "__main__":
    main()