import pandas as pd
from pathlib import Path

# custom utilities for loading and processing waveform data
from src.io_utils import load_two_column_csv, load_multi_pair_csv
from src.metrics import edge_metrics, estimate_delay, current_metrics, seu_metrics, snm_proxy


def run_analysis(data_dir):
    # make sure the input path is a Path object (easier to handle file paths)
    data_dir = Path(data_dir)

    # load raw waveform data
    # D / D2 are input-related signals, Q1B is the output/internal node
    d = load_two_column_csv(data_dir / "10T_Test_D.csv")
    d2 = load_two_column_csv(data_dir / "10T_Test_D2.csv")
    q1b = load_two_column_csv(data_dir / "QB1_TEST_CSV.csv")

    # supply current (used for power / energy estimation)
    current = load_two_column_csv(data_dir / "10T_Test_I.csv")

    # SEU file contains multiple (X, Y) pairs → each corresponds to one injection scenario
    seu = load_multi_pair_csv(data_dir / "N0_Test.csv")

    # SNM-related curve (not full butterfly, used as a proxy)
    snm = load_two_column_csv(data_dir / "Quatro_SNM_test.csv")

    # transient behavior summary
    # basic signal-level features (initial/final values, transition timing, etc.)
    transient_summary = pd.DataFrame([
        {"signal": "D", **edge_metrics(d)},
        {"signal": "D2", **edge_metrics(d2)},
        {"signal": "Q1B", **edge_metrics(q1b)},
    ])

    # delay estimation
    # estimate delay from D → Q1B using 50% threshold crossing
    # note: this is a simplified proxy (not full WL-controlled timing)
    delay_summary = pd.DataFrame([
        {"path": "D -> Q1B", **estimate_delay(d, q1b)},
    ])

    # power / energy
    # convert supply current into power using P = V * I
    # integrate over time to get energy per switching event
    power_summary = pd.DataFrame([
        {"signal": "I(VDD)", **current_metrics(current, vdd=1.1)},
    ])

    # SEU analysis
    # for each injection case, measure dip, recovery time, and disturbance severity
    seu_summary = []
    for name, df in seu.items():
        seu_summary.append({
            "scenario": name,
            **seu_metrics(df)
        })
    seu_summary = pd.DataFrame(seu_summary)

    # SNM proxy
    # since full VTC is not available, use curve-based indicators as a proxy
    snm_summary = pd.DataFrame([
        {"curve": "Quatro_SNM_test", **snm_proxy(snm)}
    ])

    # pack everything
    # return both raw signals and processed summaries for downstream analysis / plotting
    return {
        "d": d,
        "d2": d2,
        "q1b": q1b,
        "current": current,
        "seu": seu,
        "snm": snm,
        "transient_summary": transient_summary,
        "delay_summary": delay_summary,
        "power_summary": power_summary,
        "seu_summary": seu_summary,
        "snm_summary": snm_summary,
    }