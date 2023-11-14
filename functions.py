from typing import Tuple

import numpy as np
import pandas as pd


def match_bcids(dataframe1: pd.DataFrame, dataframe2: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    # Find common indexes
    common_indexes = dataframe1.index.intersection(dataframe2.index)

    # Filter DataFrames based on common indexes
    dataframe1 = dataframe1.loc[common_indexes]
    dataframe2 = dataframe2.loc[common_indexes]

    return dataframe1, dataframe2

def filter_by_cov_status(dataframe: pd.DataFrame, cov_status: int) -> pd.DataFrame:
    good_bcids_in_x = dataframe[dataframe["covStatus_X"] == cov_status]["BCID"].to_numpy()
    good_bcids_in_y = dataframe[dataframe["covStatus_Y"] == cov_status]["BCID"].to_numpy()
    
    good_bcids = good_bcids_in_x

    if good_bcids_in_x.shape != good_bcids_in_y.shape or np.any(good_bcids_in_x != good_bcids_in_y):
        good_bcids = np.intersect1d(good_bcids_in_x, good_bcids_in_y)

    dataframe = dataframe[dataframe["BCID"].isin(good_bcids)].reset_index(drop=True)

    assert dataframe["covStatus_X"].unique() == cov_status
    assert dataframe["covStatus_Y"].unique() == cov_status

    return dataframe
