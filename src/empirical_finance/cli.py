"""Run the public-data research pipeline; do not commit raw data or output tables."""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .analysis import calendar_wald, factor_regressions
from .data import factor_sample, load_sources, seasonality_sample
from .gmm import estimate_sdf


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run French-data asset-pricing replication")
    parser.add_argument("--cache", type=Path, default=Path("data/raw"))
    parser.add_argument("--output", type=Path, default=Path("outputs"))
    parser.add_argument("--offline", action="store_true", help="Never download; require cached ZIPs")
    parser.add_argument("--refresh", action="store_true", help="Redownload all French data ZIPs")
    args = parser.parse_args(argv)
    if args.refresh and args.offline:
        parser.error("--refresh and --offline cannot be combined")

    frames, source_manifest = load_sources(args.cache, offline=args.offline,
                                           refresh=args.refresh)
    factor = factor_sample(frames)
    calendar = seasonality_sample(frames)
    regressions, momentum = factor_regressions(factor)
    seasonality = calendar_wald(calendar)
    sdf = estimate_sdf(factor)

    args.output.mkdir(parents=True, exist_ok=True)
    regressions.to_csv(args.output / "factor_regressions.csv", index=False, float_format="%.10g")
    momentum.to_csv(args.output / "momentum.csv", index=False, float_format="%.10g")
    seasonality.to_csv(args.output / "seasonality.csv", index=False, float_format="%.10g")
    summary = {
        "source_archives": source_manifest,
        "return_units": "decimal (0.01 = 1 percent)",
        "calendar_sample": {"start": "1927-01", "end": "2025-12", "n": len(calendar)},
        "factor_sample": {"start": "1963-07", "end": "2026-06", "n": len(factor)},
        "factor_hac_lags": 24,
        "gmm_bartlett_lags": 6,
        "gmm_centering": False,
        "sdf_two_step": asdict(sdf),
        "interpretation": "Historical in-sample research; not an executable trading strategy."
    }
    (args.output / "manifest.json").write_text(json.dumps(summary, indent=2) + "\n",
                                               encoding="utf-8")
    print(f"Calendar: {len(calendar)} months; factors: {len(factor)} months.")
    print(f"CAPM / FF5: {len(regressions)} industry estimates + 2 momentum estimates.")
    print(f"Two-step SDF GMM: J = {sdf.j_stat:.4f}, p = {sdf.j_p_value:.4f} (df = {sdf.degrees_freedom}).")
    print(f"Wrote outputs and source hashes to {args.output}/")
    print("Compare independently with the original archived report before claiming reproduction.")


if __name__ == "__main__":
    main()
