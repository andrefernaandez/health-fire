import argparse
import os
from pathlib import Path

import django
import pandas as pd


def _split_csv_argument(value):
    if not value:
        return None

    return [item.strip() for item in value.split(",") if item.strip()]


def _split_int_argument(value):
    if not value:
        return None

    return [int(item.strip()) for item in value.split(",") if item.strip()]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run Pearson and Spearman correlations for INPE burned data and DATASUS/TABNET health data."
    )
    parser.add_argument("--start-year", type=int, default=2015)
    parser.add_argument("--end-year", type=int, default=2025)
    parser.add_argument("--lag-months", type=int, default=0)
    parser.add_argument(
        "--federative-units",
        default=None,
        help="Comma-separated state names exactly as saved in the database.",
    )
    parser.add_argument(
        "--cid-ids",
        default="38",
        help="Comma-separated CID ids. Default: 38.",
    )
    parser.add_argument(
        "--type-health-ids",
        default="43",
        help="Comma-separated health type ids. Default: 43, Internacoes.",
    )
    parser.add_argument(
        "--output",
        default="correlation_tests/results/correlation_results.csv",
        help="CSV path for the correlation summary.",
    )
    parser.add_argument(
        "--aligned-output",
        default="correlation_tests/results/aligned_monthly_data.csv",
        help="CSV path for the monthly data used in the tests.",
    )
    return parser.parse_args()


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "healthfire.settings")
    django.setup()

    from correlation_tests.services import run_correlation_tests

    args = parse_args()
    results, aligned_data = run_correlation_tests(
        start_year=args.start_year,
        end_year=args.end_year,
        federative_units=_split_csv_argument(args.federative_units),
        cid_ids=_split_int_argument(args.cid_ids),
        type_health_ids=_split_int_argument(args.type_health_ids),
        lag_months=args.lag_months,
    )

    output = Path(args.output)
    aligned_output = Path(args.aligned_output)
    output.parent.mkdir(parents=True, exist_ok=True)
    aligned_output.parent.mkdir(parents=True, exist_ok=True)

    pd.DataFrame([result.as_dict() for result in results]).to_csv(output, index=False)
    aligned_data.to_csv(aligned_output, index=False)

    print(f"Correlation results saved to: {output}")
    print(f"Aligned monthly data saved to: {aligned_output}")
    print(pd.DataFrame([result.as_dict() for result in results]).to_string(index=False))


if __name__ == "__main__":
    main()
