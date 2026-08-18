import argparse
import os

import django


def parse_args():
    parser = argparse.ArgumentParser(
        description="Validate Pearson and Spearman correlation execution."
    )
    parser.add_argument("--start-year", type=int, default=2015)
    parser.add_argument("--end-year", type=int, default=2025)
    parser.add_argument("--lag-months", type=int, default=0)
    parser.add_argument("--cid-id", type=int, default=38)
    parser.add_argument("--type-health-id", type=int, default=43)
    return parser.parse_args()


def _assert_coefficient_is_valid(result):
    if result.coefficient is None:
        raise AssertionError(f"{result.method} coefficient is empty.")

    if not -1 <= result.coefficient <= 1:
        raise AssertionError(
            f"{result.method} coefficient must be between -1 and 1. "
            f"Received: {result.coefficient}"
        )


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "healthfire.settings")
    django.setup()

    from correlation_tests.services import run_correlation_tests

    args = parse_args()
    results, aligned_data = run_correlation_tests(
        start_year=args.start_year,
        end_year=args.end_year,
        cid_ids=[args.cid_id],
        type_health_ids=[args.type_health_id],
        lag_months=args.lag_months,
    )

    methods = {result.method for result in results}
    if methods != {"pearson", "spearman"}:
        raise AssertionError(f"Expected pearson and spearman. Received: {methods}")

    if aligned_data.empty:
        raise AssertionError("Aligned monthly data is empty.")

    required_columns = {
        "period",
        "federative_unit",
        "burned_count",
        "health_cases",
        "cid_id",
        "type_health_id",
    }
    missing_columns = required_columns.difference(aligned_data.columns)
    if missing_columns:
        raise AssertionError(f"Missing aligned data columns: {missing_columns}")

    if aligned_data[["burned_count", "health_cases"]].isna().any().any():
        raise AssertionError("Aligned data has empty burned_count or health_cases values.")

    if set(aligned_data["cid_id"].unique()) != {args.cid_id}:
        raise AssertionError("Aligned data contains CID values outside the selected CID.")

    if set(aligned_data["type_health_id"].unique()) != {args.type_health_id}:
        raise AssertionError(
            "Aligned data contains health type values outside the selected type."
        )

    duplicate_health_rows = aligned_data.duplicated(
        subset=["period", "federative_unit", "cid_id", "type_health_id"]
    )
    if duplicate_health_rows.any():
        raise AssertionError(
            "Aligned data has duplicate DiseaseCase rows for the same month, state and CID."
        )

    min_year = int(aligned_data["period"].dt.year.min())
    max_year = int(aligned_data["period"].dt.year.max())
    if min_year < args.start_year or max_year > args.end_year:
        raise AssertionError(
            f"Aligned data period is outside {args.start_year}-{args.end_year}: "
            f"{min_year}-{max_year}"
        )

    for result in results:
        if result.sample_size != len(aligned_data):
            raise AssertionError(
                f"{result.method} sample_size does not match aligned data length."
            )
        _assert_coefficient_is_valid(result)

    print("Correlation validation passed.")
    print(f"Period: {min_year}-{max_year}")
    print(f"Aligned rows: {len(aligned_data)}")
    print(f"CID id: {args.cid_id}")
    print(f"Health type id: {args.type_health_id}")
    for result in results:
        print(f"{result.method}: {result.coefficient}")


if __name__ == "__main__":
    main()
