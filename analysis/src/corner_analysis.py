import pandas as pd


def load_corner_data(results_path, corners_path):
    # load results + corner conditions
    df_results = pd.read_csv(results_path)
    df_corners = pd.read_csv(corners_path)

    # merge them (they normally share a common index or id)
    df = pd.concat([df_results, df_corners], axis=1)

    return df


def basic_summary(df):
    # quick stats for poster
    return {
        "rows": len(df),
        "columns": list(df.columns)
    }


def find_worst_case(df, metric):
    # find worst case row for a given metric
    if metric not in df.columns:
        return None

    return df.loc[df[metric].idxmax()]


def find_best_sizing(df, power_col, seu_col):
    """
    simple trade-off:
    minimize power + maximize SEU robustness
    """
    df = df.copy()

    # normalize
    df["power_norm"] = df[power_col] / df[power_col].max()
    df["seu_norm"] = df[seu_col] / df[seu_col].max()

    # trade-off score (you can tweak weights)
    df["score"] = df["power_norm"] - df["seu_norm"]

    return df.sort_values("score").iloc[0]