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
