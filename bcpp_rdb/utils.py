import hashlib

import numpy as np
import pandas as pd


def identity256(row, column_name=None):
    identity256 = np.nan
    column_name = column_name or 'identity'
    if pd.notnull(row[column_name]):
        identity256 = hashlib.sha256(identity(row, column_name)).digest().encode("hex")
    return identity256
