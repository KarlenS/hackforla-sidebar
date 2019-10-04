import numpy as np
import pandas as pd

from shapely import wkt, Point

def fill_placeholder_1900(df):
    return df.replace(to_replace=pd.to_datetime('1900'),value=pd.NaT)

def fill_placeholder_1900_col(df):
    dt_cols = ['CreatedDate','UpdatedDate','ServiceDate','ClosedDate']
    for col in dt_cols:
        df[col] = df[col].replace(to_replace=pd.to_datetime('1900'),value=pd.NaT)

def fill_placeholder_1900_col(df):
    dt_cols = ['CreatedDate','UpdatedDate','ServiceDate','ClosedDate']
    for col in dt_cols:
        df[col] = df[col].replace(to_replace=pd.to_datetime('1900'),value=pd.NaT)

def ddiff2days(ddiff):
    if not pd.isnull(ddiff):
        return pd.Timedelta.total_seconds(ddiff)/(24.*3600)
    else:
        return np.NaN

def to_points(p):
    if type(p) == float:
        return p
    else:
        return wkt.loads('Point{}'.format(p.replace(',',' ')))
