"""Quick checks for daily market parquet coverage and alignment."""

from __future__ import annotations

from pathlib import Path

import ast

import pandas as pd


def main() -> None:
    base = Path("data/processed/market/daily")
    files = sorted(base.glob("*.parquet"))
    results = []

    def normalize(col):
        if isinstance(col, tuple) and col:
            return col[0]
        if isinstance(col, str) and col.startswith("("):
            try:
                parsed = ast.literal_eval(col)
                if isinstance(parsed, tuple) and parsed:
                    return parsed[0]
            except Exception:
                return col
        return col

    for fp in files:
        df = pd.read_parquet(fp)
        df.columns = [normalize(c) for c in df.columns]
        df["date"] = pd.to_datetime(df["date"], utc=True)
        df = df.sort_values("date")
        gaps = df["date"].diff().dt.days.dropna()
        gaps_over3 = gaps[gaps > 3]
        results.append(
            (
                fp.stem,
                df["date"].min().date(),
                df["date"].max().date(),
                len(df),
                len(gaps_over3),
            )
        )
        if not gaps_over3.empty:
            print(f"{fp.stem} gaps >3 days: {gaps_over3.to_list()}")

    for row in results:
        print(row)

    ref = pd.read_parquet(base / "SPY.parquet")
    ref.columns = [normalize(c) for c in ref.columns]
    ref_dates = pd.to_datetime(ref["date"], utc=True)
    common_len = len(ref_dates)
    print("SPY rows", common_len)
    for fp in files:
        df = pd.read_parquet(fp)
        df.columns = [normalize(c) for c in df.columns]
        dates = pd.to_datetime(df["date"], utc=True)
        overlap = len(pd.Index(ref_dates).intersection(pd.Index(dates)))
        if fp.stem != "XLC":
            if overlap != common_len:
                print("Misaligned overlap", fp.stem, overlap)
        else:
            print("XLC overlap with SPY", overlap, "of", len(dates))


if __name__ == "__main__":
    main()
