import numpy as np
import pandas as pd
import pytest

from empirical_finance.data import parse_monthly_csv, require_window

MOCK = """Kenneth French style test only
Monthly returns
,Oil,Banks,Txtls,Toys,Rtail
202601, 1.00, 2.00, -99.99, 4.00, 5.00
202602, -1.00, 1.50, 3.00, -999, 0.50

Annual returns
,Oil,Banks,Txtls,Toys,Rtail
2026, 7, 8, 9, 10, 11
"""


def test_parses_monthly_only_and_converts_units():
    df = parse_monthly_csv(MOCK)
    assert list(df.index.astype(str)) == ["2026-01", "2026-02"]
    assert df.loc[pd.Period("2026-01"), "Oil"] == pytest.approx(0.01)
    assert df.loc[pd.Period("2026-02"), "Oil"] == pytest.approx(-0.01)
    assert np.isnan(df.iloc[0]["Txtls"])
    assert np.isnan(df.iloc[1]["Toys"])


def test_sample_rejects_missing_data():
    df = parse_monthly_csv(MOCK)
    with pytest.raises(ValueError, match="Missing required monthly data"):
        require_window(df, "2026-01", "2026-02", ["Toys"])


def test_sample_rejects_unknown_column():
    df = parse_monthly_csv(MOCK)
    with pytest.raises(ValueError, match="Missing expected French columns"):
        require_window(df, "2026-01", "2026-02", ["NotAnIndustry"])


def test_parser_requires_header_and_monthly_data():
    with pytest.raises(ValueError):
        parse_monthly_csv("Nothing to parse here")
    with pytest.raises(ValueError):
        parse_monthly_csv("No header\n202601,1.0,2.0")
