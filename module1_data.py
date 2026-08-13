"""Module 1: validate the single healthy NASA data file and split 40/30/30."""

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "data.csv"
FEATURES = [
    "alt", "Mach", "TRA", "T2", "T24", "T30", "T48", "P15", "P2", "P21", "P24", "Ps30",
    "P40", "P50", "Nf", "Nc", "Wf", "T40", "P30", "P45", "W21", "W22", "W25", "W31",
    "W32", "W48", "W50", "SmFan", "SmLPC", "SmHPC", "phi",
]
TARGET = "T50"
SAMPLE_INTERVAL_SECONDS = 1
FORECAST_STEPS = 600


def robust_sd(values):
    values = np.asarray(values, dtype=float)
    median = float(np.median(values))
    return max(1.4826 * float(np.median(np.abs(values - median))), 1e-12)


def isolated_spikes(frame):
    bad = np.zeros(len(frame), dtype=bool)
    for column in FEATURES + [TARGET]:
        values = frame[column].to_numpy(dtype=float)
        difference_sd = robust_sd(np.diff(values))
        for index in range(2, len(values) - 2):
            neighbors = np.r_[values[index - 2:index], values[index + 1:index + 3]]
            local_sd = max(robust_sd(neighbors), 0.10 * difference_sd)
            rejoined = abs(values[index - 1] - values[index + 1]) <= 4.0 * difference_sd
            if rejoined and abs(values[index] - np.median(neighbors)) > 8.0 * local_sd:
                bad[index] = True
    return bad


def load_and_split():
    raw = pd.read_csv(DATA_FILE)
    if raw.columns.tolist() != FEATURES + [TARGET]:
        raise ValueError("data.csv does not match the N-CMAPSS extraction schema")
    raw = raw.apply(pd.to_numeric, errors="raise")
    finite = np.isfinite(raw.to_numpy(dtype=float)).all(axis=1)
    duplicate = raw.duplicated().to_numpy()
    spike = isolated_spikes(raw)
    # NASA already labels every extracted row as health_state=1. Do not delete
    # valid healthy operating modes merely because a regression model dislikes
    # them; only corrupt/duplicate/isolated-spike rows are removed here.
    clean = raw.loc[finite & ~duplicate & ~spike].reset_index(drop=True)

    first_end = int(0.40 * len(clean)); second_end = int(0.70 * len(clean))
    parts = clean.iloc[:first_end], clean.iloc[first_end:second_end], clean.iloc[second_end:]
    print(f"Module 1 PASS | NASA-labelled healthy rows={len(clean)} | removed={len(raw)-len(clean)} | split={list(map(len, parts))}")
    return clean, parts[0].copy(), parts[1].copy(), parts[2].copy()


if __name__ == "__main__":
    load_and_split()
