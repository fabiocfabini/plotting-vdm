from typing import List, Dict, Tuple
from typing import Union, Optional, ClassVar
from pathlib import Path
from datetime import datetime

import re

import pandas as pd


class ScanResults:
    """
    The ScanResults class is designed to process data from a specified path, 
    extracting information related to detectors, fits, and corrections. It then 
    organizes this data in a dictionary of fits to DataFrames. Each DataFrame
    contains the fit results and cross section results for each detector and
    correction for the specified fit.

    Parameters
    ----------
    path : Union[pathlib.Path,str]
        A path-like to the directory containing the fill results.
        Stem should match r'^\d_*' regex.
    fits : List[str]
        A list of all the fit results to read into memory.
        Example: SG, SGConst, DG
    detectors : Optional[List[str]]
        A list of all the detector results to read into memory.
        If None, all detectors in the path will be read.
        Example: PLT, BCM1F
    corrections : Optional[List[str]]
        A list of all the correction results to read into memory.
        If None, all corrections in the path will be read.
        Example: noCorr, Background
    name : str
        The name of the scan.
    energy : float
        The energy of the scan.
    energy_unit : str
        The unit of the energy of the scan.

    Attributes
    -----
    id_str : str
        The id of the scan. Ex: 8381_11Nov22_004152_11Nov22_010424
    results : Dict[str, pd.DataFrame]
        A dictionary containing the fit results and cross section results DataFrames for each fit.
    fill_number : int
        The fill number extracted from the path.
    fits : List[str]
        A list of all the fit results to read into memory.
    detectors : List[str]
        A list of all the detector results to read into memory.
    corrections : List[str]
        A list of all the correction results to read into memory.
    name : str
        The name of the scan. Ex: vdM1
    energy : float
        The energy of the scan.
    energy_unit : str
        The unit of the energy of the scan.
    year: int
        The year of the scan.

    Examples
    --------
    Instantiating ScanResults.

    >>> # You must be in lxplus for this path to work
    >>> path = "<path-to>/output/analysed_data/<scan-name>"
    >>> fits = ["SG", "DG"]
    >>> detectors = ["PLT", "BCM1F"]
    >>> corrections = ["noCorr", "Background"]
    >>> results = ScanResults(path, fits, detectors, corrections)
    >>> results
    Fill Results for '<path-to>/output/analysed_data/<scan-name>':
        fits: ['SG', 'DG']
        detectors: ['PLT', 'BCM1F']
        corrections: ['noCorr', 'Background']
    """

    _timestamp_format = "%d%b%y_%H%M%S"
    _detector_prefixes: ClassVar[Tuple[str, ...]] = (
        "PLT", "BCM1F", "BCM1FUTCA", "HFET", "HFOC"
    )
    _correction_prefixes: ClassVar[Tuple[str, ...]] = (
        "noCorr", "Background"
    )  # what other correction prefixes are there?
    _quantity_to_latex: ClassVar[Dict[str, str]] = {
        "CapSigma_X": r"$\sigma_X$",
        "CapSigma_Y": r"$\sigma_Y$",
        "peak_X": r"Pea$k_X$",
        "peak_Y": r"Pea$k_Y$",
        "xsec": r"$\sigma_{vis}$",
    }

    def __init__(self,
                path: Union[Path, str],
                fits: List[str],
                detectors: Optional[List[str]] = None,
                corrections: Optional[List[str]] = None,
                name: str = "",
                energy: float = 0.0,
                energy_unit: str = "GeV",
                ) -> None:
        if isinstance(path, str):
            self._path = Path(path).absolute()
        else:
            self._path = path.absolute()

        self.fits = fits
        self.name = name
        self.energy = energy
        self.energy_unit = energy_unit

        self._iter_detectors = detectors is None
        self._detectors = [] if self._iter_detectors else detectors
        assert self._detectors is not None

        self._iter_corrections = corrections is None
        self._corrections = [] if self._iter_corrections else corrections
        assert self._corrections is not None

        self.fill_number = self._get_fill_number()
        self.start, self.end = self._get_scan_times()

        self.results: Dict[str, pd.DataFrame] = {}
        self._collect_results()

    @property
    def path(self) -> Path:
        return self._path

    @property
    def id_str(self) -> str:
        return self._path.stem

    @property
    def corrections(self) -> List[str]:
        assert self._corrections is not None
        return self._corrections

    @property
    def detectors(self) -> List[str]:
        assert self._detectors is not None
        return self._detectors

    @property
    def energy_str(self) -> str:
        return f"{self.energy} {self.energy_unit}"

    def is_common_column(self, column: str) -> bool:
        """Checks if the column is common to all fits.

        Arguments
        ---------
            column : str
                The column to check.

        Returns
        -------
            bool
                Tr  ue if the column is common to all fits.
        """
        return all(column in result.columns for result in self.results.values())

    @classmethod
    def get_quantity_latex(cls, quantity: str) -> str:
        """Returns the LaTeX respresentation of the quantity.

        Arguments
        ---------
            quantity : str
                The quantity to get the LaTeX representation of.

        Returns
        -------
            str
                The LaTeX representation of the quantity.

        Raises
        ------
            ValueError
                If the quantity is not recognized or is not valid.
        """

        if quantity not in cls._quantity_to_latex:
            raise ValueError(f"Quantity '{quantity}' is not recognized.")

        return cls._quantity_to_latex[quantity]

    @classmethod
    def get_quantity_and_error(cls, quantity: str) -> Tuple[str, str]:
        """Returns the quantity and error for the given quantity.

        Arguments
        ---------
            quantity : str
                The quantity to get the quantity and error for.

        Returns
        -------
            Tuple[str, str]
                The quantity and error for the given quantity.
        """
        if quantity.endswith("_X"):
            return quantity, quantity.replace("_X", "Err_X")
        elif quantity.endswith("_Y"):
            return quantity, quantity.replace("_Y", "Err_Y")
        else:
            return quantity, f"{quantity}Err"

    def _get_fill_number(self) -> int:
        result = re.match(r"^(\d)*", self._path.stem)
        if not result:
            raise ValueError(f"Could not extract fill number from path '{self._path}'.")

        return int(result.group())

    def _get_scan_times(self) -> Tuple[datetime, datetime]:
        result = re.search("\d+_(\d{2}\w+\d{2}_\d{6})_(\d{2}\w+\d{2}_\d{6})", self._path.stem)

        if not result:
            raise ValueError(f"Could not extract scan times from path '{self._path}'.")
        
        time_start, time_end = result.groups()

        start = datetime.strptime(time_start, self._timestamp_format)
        end = datetime.strptime(time_end, self._timestamp_format)

        return start, end

    def _process_fit_results(self, fit_results: List[pd.DataFrame]) -> pd.DataFrame:
        results = pd.concat(fit_results)\
                        .sort_index()\
                        .pivot_table(
                            index=["BCID", "detector", "correction"],
                            columns="Type"
                        ).reset_index()

        results.columns = pd.Index([
            f"{name}_{plane}" if plane else name
            for name, plane in results.columns
        ])

        return results

    def _process_sigvis_results(self, sigvis_results: List[pd.DataFrame]) -> pd.DataFrame:
        results = pd.concat(sigvis_results)\
                    .sort_index()\
                    .drop(columns=["XscanNumber_YscanNumber", "Type"])

        return results

    def _collect_results(self) -> None:
        if self._iter_detectors:
            folders = [folder.stem for folder in self._path.iterdir() if folder.is_dir()]
            self._detectors = [folder for folder in folders if folder.startswith(self._detector_prefixes)]

        for fit in self.fits:
            per_detector_fit_results: List[pd.DataFrame] = []
            per_detector_sigvis_results: List[pd.DataFrame] = []

            assert self._detectors is not None
            for detector in self._detectors:
                detector_fit_results, detector_sigvis_results = self._read_detector_results(fit, detector)

                per_detector_fit_results.append(detector_fit_results)
                per_detector_sigvis_results.append(detector_sigvis_results)

            fit_results = self._process_fit_results(per_detector_fit_results)
            sigvis_results = self._process_sigvis_results(per_detector_sigvis_results)

            self.results[fit] = fit_results.merge(sigvis_results, on=["BCID", "detector", "correction"])

    def _read_detector_results(self, fit: str, detector: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        if self._iter_corrections:
            folders = [folder.stem for folder in (self._path / detector / "results").iterdir() if folder.is_dir()]
            self._corrections = [folder for folder in folders if folder.startswith(self._correction_prefixes)]

        per_correction_fit_results: List[pd.DataFrame] = []
        per_correction_sigvis_results: List[pd.DataFrame] = []

        assert self._corrections is not None
        for correction in self._corrections:

            fit_result = self._read_fit_result(fit, detector, correction)
            sigvis_result = self._read_sigvis_result(fit, detector, correction)

            per_correction_fit_results.append(fit_result)
            per_correction_sigvis_results.append(sigvis_result)

        fit_results = pd.concat(per_correction_fit_results, ignore_index=True)
        fit_results["detector"] = detector

        sigvis_results = pd.concat(per_correction_sigvis_results, ignore_index=True)
        sigvis_results["detector"] = detector

        return fit_results, sigvis_results

    def _read_fit_result(self, fit: str, detector: str, correction: str) -> pd.DataFrame:
        fit_result_path = self._path / detector / "results" / correction / f"{fit}_FitResults.csv"
        fit_result = pd.read_csv(fit_result_path)

        fit_result["correction"] = correction

        return fit_result

    def _read_sigvis_result(self, fit: str, detector: str, correction: str) -> pd.DataFrame:
        sigvis_result_path = self._path / detector / "results" / correction / f"LumiCalibration_{detector}_{fit}_{self.fill_number}.csv"
        sigvis_result = pd.read_csv(sigvis_result_path)

        sigvis_result["correction"] = correction

        return sigvis_result

    def __str__(self) -> str:
        output =  f"Fill Results for '{self._path}':\n\t"
        output += f"name: {self.name}\n\t"
        output += f"energy: {self.energy_str}\n\t"
        output += f"fill number: {self.fill_number}\n\t"
        output += f"fits: {self.fits}\n\t"
        output += f"detectors: {self._detectors}\n\t"
        output += f"corrections: {self._corrections}\n\t"
        output += f"timestamp: {self.start} - {self.end}"

        return output

    def __repr__(self) -> str:
        return self.__str__()


if __name__ == "__main__":
    scan_results = ScanResults(
        path="../output/analysed_data/8381_11Nov22_004152_11Nov22_010424",
        fits=["SG", "DG"],
        name="vdM1",
        energy=13.6,
        energy_unit="TeV",
    )
