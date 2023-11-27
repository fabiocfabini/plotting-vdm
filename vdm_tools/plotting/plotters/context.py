from typing import Tuple


class PlotContext(dict):
    """Class that contains the context of the plot.
    It is used to pass information from the VdMPlotter to the plot strategy
    and between different plot strategy methods.

    Attributes
    ----------
    plotter : VdMPlotter
        The plotter that is currently being used.
    current_fit, current_detector, current_correction : str
        The current fit, detector and correction that are being plotted.
        The plot strategy can use these attributes to:
        - filter the data
        - add a label to the plot

    Methods
    -------
    is_in_fit_loop() -> bool
        Return True if we the plotter is currently in a fit loop.
    is_in_detector_loop() -> bool
        Return True if we the plotter is currently in a detector loop.
    is_in_correction_loop() -> bool
        Return True if we the plotter is currently in a correction loop.

    Notes
    -----
    The PlotContext derives from dict and can be used as such. However, it is
    recommended to use the provided properties and methods to access the special
    attributes. This ensures that the special attributes are not overwritten
    accidentally.
    """
    __SPECIAL_ATTRS = {
        "plotter": None,
        "current_fit": "",
        "current_detector": "",
        "current_correction": "",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reset()

    @property
    def plotter(self) -> str:
        """The plotter that is currently being used.
        """
        return self["plotter"]

    @plotter.setter
    def plotter(self, value):
        self["plotter"] = value

    @property
    def current_fit(self) -> str:
        """The current fit that is being plotted.
        """
        return self["current_fit"]

    @current_fit.setter
    def current_fit(self, value):
        self["current_fit"] = value

    @property
    def current_detector(self) -> str:
        """The current detector that is being plotted.
        """
        return self["current_detector"]

    @current_detector.setter
    def current_detector(self, value):
        self["current_detector"] = value

    @property
    def current_correction(self) -> str:
        """The current correction that is being plotted.
        """
        return self["current_correction"]

    @current_correction.setter
    def current_correction(self, value):
        self["current_correction"] = value

    @property
    def special_attrs(self) -> Tuple[str]:
        """Return the list of special attributes."""
        return self.__SPECIAL_ATTRS

    def is_in_fit_loop(self) -> bool:
        """Return True if the plotter is currently in a fit loop."""
        return self.current_fit != ""

    def is_in_detector_loop(self) -> bool:
        """Return True if the plotter is currently in a detector loop."""
        return self.current_detector != ""

    def is_in_correction_loop(self) -> bool:
        """Return True if the plotter is currently in a correction loop."""
        return self.current_correction != ""

    def reset(self):
        """Reset the context to its initial state.
        All special attributes are set to an empty string.
        """
        for attr, default in self.__SPECIAL_ATTRS.items():
            self[attr] = default
