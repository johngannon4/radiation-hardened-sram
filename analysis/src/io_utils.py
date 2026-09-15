from pathlib import Path
import pandas as pd


def load_two_column_csv(path):
    # basic loader for standard waveform exports (time, value)
    df = pd.read_csv(path)

    # normalize column names so downstream code is consistent
    df = df.rename(columns={
        df.columns[0]: "time",
        df.columns[1]: "value"
    })

    # make sure everything is numeric (Cadence export sometimes includes text)
    df["time"] = pd.to_numeric(df["time"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    # drop invalid rows and reset index
    df = df.dropna().reset_index(drop=True)

    return df


def load_multi_pair_csv(path):
    # used for files where data comes in (X, Y) pairs
    # e.g. multiple SEU injection cases in a single CSV
    raw = pd.read_csv(path)

    # force all columns to numeric (ignore anything weird)
    for col in raw.columns:
        raw[col] = pd.to_numeric(raw[col], errors="coerce")

    results = {}
    cols = list(raw.columns)

    # iterate through columns in pairs: (X1, Y1), (X2, Y2), ...
    for i in range(0, len(cols), 2):
        x_col = cols[i]
        y_col = cols[i + 1]

        # clean up name (Cadence usually adds " X" suffix)
        name = x_col.replace(" X", "").strip()

        df = raw[[x_col, y_col]].copy()
        df.columns = ["time", "value"]

        # remove NaNs so each scenario is clean
        df = df.dropna().reset_index(drop=True)

        # store each scenario separately
        results[name] = df

    return results