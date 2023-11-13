from __future__ import annotations

from dataclasses import dataclass

from .corrections import CORRECTIONS


class AutoAttrList(type):
    """This Metaclass automatically creates a list of all attributes 
    of a class that are prefixed with an '_{class_name}' (meaning they 
    start with a dunderscore)

    Only considers the attributes that are defined in the __annotations__!
    """

    def __new__(cls, name, bases, dct):
        instance = super().__new__(cls, name, bases, dct)

        instance._auto_attr_list = [
            attr_name
            for attr_name in instance.__annotations__.keys()
            if attr_name.startswith(f"_{name}")
        ]

        return instance


@dataclass
class TitleBuilder(metaclass=AutoAttrList):
    __scan_name: str = ""
    __info: str = ""
    __axis: str = ""
    __correction: str = ""
    __detector: str = ""
    __fit: str = ""

    def build(self) -> str:
        title_parts = self._build_title_parts()

        return ", ".join(title_parts)

    def set_info(self, info: str) -> TitleBuilder:
        self.__info = info
        return self

    def set_scan_name(self, scan_name: str) -> TitleBuilder:
        self.__scan_name = scan_name
        return self

    def set_correction(self, correction: str) -> TitleBuilder:
        for name in correction.split("_"):
            self.__correction += f"{CORRECTIONS[name]}_"

        # Remove last underscore
        self.__correction = self.__correction[:-1]
        return self

    def set_detector(self, detector: str) -> TitleBuilder:
        self.__detector = detector
        return self

    def set_fit(self, fit: str) -> TitleBuilder:
        self.__fit = fit
        return self

    def set_axis(self, axis: str) -> TitleBuilder:
        self.__axis = axis
        return self

    def _build_title_parts(self) -> list[str]:
        return [
            part
            for part in map(lambda attr: getattr(self, attr), self._auto_attr_list)
            if part
        ]
