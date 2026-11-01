"""Load Kenneth French monthly CSV archives, without storing third-party data in git.

French CSV archives contain prose, monthly rows and often separate annual rows.
Only the *first contiguous YYYYMM block* is read. Returns are decimal, not percent.
"""
from __future__ import annotations

import csv
import hashlib
import io
import re
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

FRENCH_BASE = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp"
SOURCES = {
    "industries": "49_Industry_Portfolios_CSV.zip",
    "five_factors": "F-F_Research_Data_5_Factors_2x3_CSV.zip",
    "momentum": "F-F_Momentum_Factor_CSV.zip",
}
INDUSTRIES = {"Oil": "Oil", "Banks": "Banks", "Textiles": "Txtls",
              "Toys": "Toys", "Retail": "Rtail"}
FACTOR_COLUMNS = ["Mkt-RF", "SMB", "HML", "RMW", "CMA", "RF"]
MONTH_ROW = re.compile(r"^\s*(\d{6})\s*,")
MISSING_SENTINELS = (-99.99, -999.0, -999.99)


def parse_monthly_csv(text: str) -> pd.DataFrame:
    """Read the first French-style monthly data block as decimal returns.

    Reject malformed dates, columns, duplicates and missing headers rather than
    guessing. Annual blocks (YYYY) and trailing source notes are not included.
    """
    lines = text.lstrip("\ufeff").splitlines()
    first = next((i for i, line in enumerate(lines) if MONTH_ROW.match(line)), None)
    if first is None:
        raise ValueError("No YYYYMM monthly observations found")
    example = next(csv.reader([lines[first]]))
    header = None
    for line in reversed(lines[:first]):
        fields = next(csv.reader([line]))
        if len(fields) == len(example) and fields[0].strip() == "" and any(
            col.strip() for col in fields[1:]
        ):
            header = fields
            break
    if header is None:
        raise ValueError("CSV table header not found")
    names = [x.strip() for x in header[1:]]
    if len(set(names)) != len(names) or not all(names):
        raise ValueError("Duplicate or blank dataset columns")
    dates, values = [], []
    for line in lines[first:]:
        if not MONTH_ROW.match(line):
            break
        parts = next(csv.reader([line]))
        if len(parts) != len(names) + 1:
            raise ValueError("Malformed monthly row: incorrect number of fields")
        dates.append(parts[0].strip())
        values.append(parts[1:])
    if not dates:
        raise ValueError("Monthly data block is empty")
    index = pd.to_datetime(dates, format="%Y%m", errors="raise").to_period("M")
    if index.has_duplicates or not index.is_monotonic_increasing:
        raise ValueError("Duplicate or unsorted monthly dates")
    data = pd.DataFrame(values, index=index, columns=names)
    for name in names:
        data[name] = pd.to_numeric(data[name].str.strip(), errors="raise")
    data = data.replace(list(MISSING_SENTINELS), np.nan).astype(float) / 100.0
    data.index.name = "month"
    return data


def read_french_archive(raw: bytes) -> pd.DataFrame:
    """Read CSV inside a zipped French data download, without extracting files."""
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        names = [name for name in zf.namelist() if name.lower().endswith(".csv")]
        if len(names) != 1:
            raise ValueError("Expected exactly one CSV inside the French ZIP")
        with zf.open(names[0]) as f:
            contents = f.read().decode("utf-8-sig", errors="replace")
    return parse_monthly_csv(contents)


def load_sources(cache_dir: Path, *, refresh: bool = False,
                 offline: bool = False) -> tuple[dict[str, pd.DataFrame], dict[str, dict]]:
    """Download/cache public ZIPs and record the SHA-256 of each specific vintage."""
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    frames, manifest = {}, {}
    for key, filename in SOURCES.items():
        path = cache_dir / filename
        url = f"{FRENCH_BASE}/{filename}"
        if refresh or not path.is_file():
            if offline:
                raise FileNotFoundError(f"Offline cache is missing: {path}")
            request = urllib.request.Request(url, headers={"User-Agent": "academic-research-example/0.1"})
            try:
                with urllib.request.urlopen(request, timeout=40) as response:
                    raw = response.read()
            except Exception as error:
                raise RuntimeError(f"Could not download {url}: {error}") from error
            # A failed/HTML response should never overwrite a valid ZIP cache.
            frame = read_french_archive(raw)
            path.write_bytes(raw)
        else:
            raw = path.read_bytes()
            frame = read_french_archive(raw)
        frames[key] = frame
        manifest[key] = {
            "source": url,
            "archive_sha256": hashlib.sha256(raw).hexdigest(),
            "first_month": str(frame.index.min()),
            "last_month": str(frame.index.max()),
            "observations": int(len(frame)),
        }
    return frames, manifest


def require_window(frame: pd.DataFrame, start: str, end: str,
                   columns: list[str]) -> pd.DataFrame:
    """Select every month in a closed window; fail on gaps or NA observations."""
    absent = sorted(set(columns) - set(frame.columns))
    if absent:
        raise ValueError(f"Missing expected French columns: {absent}")
    expected = pd.period_range(start, end, freq="M")
    selected = frame.reindex(expected)[columns]
    if selected.isna().any().any():
        bad = selected.index[selected.isna().any(axis=1)].astype(str).tolist()[:6]
        raise ValueError(f"Missing required monthly data, first months: {bad}")
    selected.index.name = "month"
    return selected


def factor_sample(frames: dict[str, pd.DataFrame], start: str = "1963-07",
                  end: str = "2026-06") -> pd.DataFrame:
    """Five industry excess returns + five factors + momentum, in decimals."""
    industries = require_window(frames["industries"], start, end,
                                list(INDUSTRIES.values())).rename(
        columns={code: title for title, code in INDUSTRIES.items()})
    factors = require_window(frames["five_factors"], start, end, FACTOR_COLUMNS)
    mom = require_window(frames["momentum"], start, end, ["Mom"])
    return pd.concat([industries, factors, mom], axis=1)


def seasonality_sample(frames: dict[str, pd.DataFrame], start: str = "1927-01",
                       end: str = "2025-12") -> pd.DataFrame:
    """Monthly raw returns (not excess returns) for month-of-year tests."""
    return require_window(frames["industries"], start, end,
                          list(INDUSTRIES.values())).rename(
        columns={code: title for title, code in INDUSTRIES.items()})
