from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Sequence

import matplotlib.pyplot as plt

from plotting_vdm.scan_results import ScanResults


class Plotter(ABC):
    @abstractmethod
    def plot(self, result: ScanResults):
        pass

    def plot_many(self, results: Sequence[ScanResults]):
        for result in results:
            self(result)

    def __call__(self, result: ScanResults):
        plt.figure()
        self.plot(result)
        plt.close()
