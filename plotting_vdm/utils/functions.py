from typing import Tuple

import numpy as np
import pandas as pd


def match_bcids(dataframe1: pd.DataFrame, dataframe2: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Match BCIDs of two DataFrames.
    This function expects that both DataFrames the BCID values as their index.
    From there, it will return two DataFrames with matching BCIDs.

    Parameters
    ----------
    dataframe1 : pd.DataFrame
        First DataFrame.
    dataframe2 : pd.DataFrame
        Second DataFrame.

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame]
        Tuple containing two DataFrames with matching BCIDs in their index.

    Examples
    --------
    >>> import pandas as pd
    >>> df1 = pd.DataFrame({"BCID": [1, 2, 4, 5, 7], "Values": [1, 2, 3, 4, 5]}).set_index("BCID")
    >>> df1
          Values
    BCID        
    1          1
    2          2
    4          3
    5          4
    7          5
    >>> df2 = pd.DataFrame({"BCID": [1, 2, 3, 6, 7], "Values": [1, 2, 3, 4, 5]}).set_index("BCID")
    >>> df2
          Values
    BCID        
    1          1
    2          2
    3          3
    6          4
    7          5
    >>> df1, df2 = match_bcids(df1, df2)
    >>> df1
          Values
    BCID        
    1          1
    2          2
    7          5
    >>> df2
          Values
    BCID
    1          1
    2          2
    7          5
    """
    # Find common indexes
    common_indexes = dataframe1.index.intersection(dataframe2.index)

    # Filter DataFrames based on common indexes
    dataframe1 = dataframe1.loc[common_indexes]
    dataframe2 = dataframe2.loc[common_indexes]

    return dataframe1, dataframe2
