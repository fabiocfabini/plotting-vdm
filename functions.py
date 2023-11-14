from typing import Tuple

import numpy as np
import pandas as pd


def match_bcids(dataframe1: pd.DataFrame, dataframe2: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    if not dataframe2["BCID"].equals(dataframe1["BCID"]):
        bcid_filter = np.intersect1d(dataframe2["BCID"], dataframe1["BCID"])

        dataframe1 = dataframe1[dataframe1["BCID"].isin(bcid_filter)].reset_index(drop=True)
        dataframe2 = dataframe2[dataframe2["BCID"].isin(bcid_filter)].reset_index(drop=True)

    return dataframe1, dataframe2