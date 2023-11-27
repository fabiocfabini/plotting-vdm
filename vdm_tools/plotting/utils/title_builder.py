from __future__ import annotations
from dataclasses import dataclass

from vdm_tools.constants import CORRECTIONS


class AutoAttrList(type):
    """This Metaclass automatically creates a list of all attributes 
    of a class that are prefixed with an '_' (meaning they start with an underscore)

    Only considers the attributes that are defined in the __annotations__!
    """

    def __new__(cls, name, bases, dct):
        instance = super().__new__(cls, name, bases, dct)

        instance._auto_attr_list = [
            attr_name
            for attr_name in instance.__annotations__.keys()
            if attr_name.startswith("_")
        ]

        return instance


@dataclass
class TitleBuilder(metaclass=AutoAttrList):
    """Builds the title of a plot.
    The title is built by concatenating the values of the private attributes
    (i.e. attributes that start with an underscore) that are not empty.

    Methods
    -------
    build()
        Builds the title string with the current values of the attributes.
    set_info(info)
        Sets the info attribute.
    set_scan_name(scan_name)
        Sets the scan_name attribute.
    set_correction(correction)
        Sets the correction attribute.
    set_detector(detector)
        Sets the detector attribute.
    set_fit(fit)
        Sets the fit attribute.
    set_axis(axis)
        Sets the axis attribute.

    Example
    -------
    >>> builder = TitleBuilder() # Create a new TitleBuilder instance
    >>> builder = builder.set_fit("SG") # Set the fit attribute
    >>> builder = builder.set_info("8381") # Set the info attribute
    >>> builder = builder.set_detector("PLT") # Set the detector attribute
    >>> builder = builder.set_correction("Background_BeamBeam_DynamicBeta") # Set the correction attribute
    >>> builder.build() # Build the title string
    '8381, BG_BB_DB, PLT, SG'
    """
    _scan_name: str = ""
    _info: str = ""
    _axis: str = ""
    _correction: str = ""
    _detector: str = ""
    _fit: str = ""

    def build(self) -> str:
        """Builds the title string with the current values of the attributes.

        Returns
        -------
        str
            The title string.
        """
        title_parts = self._build_title_parts()

        return ", ".join(title_parts)

    def set_info(self, info: str) -> TitleBuilder:
        """Sets the info attribute.

        Parameters
        ----------
        info : str
            The info attribute.

        Returns
        -------
        TitleBuilder
            The altered TitleBuilder instance.
        """
        self._info = info
        return self

    def set_scan_name(self, scan_name: str) -> TitleBuilder:
        """Sets the scan_name attribute.

        Parameters
        ----------
        scan_name : str
            The scan_name attribute.

        Returns
        -------
        TitleBuilder
            The altered TitleBuilder instance.
        """
        self._scan_name = scan_name
        return self

    def set_correction(self, correction: str) -> TitleBuilder:
        """Sets the correction attribute.

        Parameters
        ----------
        correction : str
            The correction attribute.

        Returns
        -------
        TitleBuilder
            The altered TitleBuilder instance.
        """
        self._correction = "_".join([
            CORRECTIONS[name] for name in correction.split("_")
        ])
        return self

    def set_detector(self, detector: str) -> TitleBuilder:
        """Sets the detector attribute.

        Parameters
        ----------
        detector : str
            The detector attribute.

        Returns
        -------
        TitleBuilder
            The altered TitleBuilder instance.
        """
        self._detector = detector
        return self

    def set_fit(self, fit: str) -> TitleBuilder:
        """Sets the fit attribute.

        Parameters
        ----------
        fit : str
            The fit attribute.

        Returns
        -------
        TitleBuilder
            The altered TitleBuilder instance.
        """
        self._fit = fit
        return self

    def set_axis(self, axis: str) -> TitleBuilder:
        """Sets the axis attribute.

        Parameters
        ----------
        axis : str
            The axis attribute.

        Returns
        -------
        TitleBuilder
            The altered TitleBuilder instance.
        """
        self._axis = axis
        return self

    # pylint: disable=E1101
    def _build_title_parts(self) -> list[str]:
        return [
            part
            for part in map(lambda attr: getattr(self, attr), self._auto_attr_list)
            if part
        ]
