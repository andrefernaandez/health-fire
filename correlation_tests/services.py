from dataclasses import dataclass
import unicodedata
from typing import Iterable, Optional

import pandas as pd
from django.db.models import Count
from django.db.models.functions import TruncMonth

from burned.models import Burned
from disease_cases.models import DiseaseCase

DEFAULT_CID_IDS = (38,)
DEFAULT_TYPE_HEALTH_IDS = (43,)


@dataclass(frozen=True)
class CorrelationResult:
    method: str
    coefficient: Optional[float]
    sample_size: int
    start_year: Optional[int]
    end_year: Optional[int]
    lag_months: int

    def as_dict(self):
        return {
            "method": self.method,
            "coefficient": self.coefficient,
            "sample_size": self.sample_size,
            "start_year": self.start_year,
            "end_year": self.end_year,
            "lag_months": self.lag_months,
        }


def _correlation_coefficient(dataframe, method):
    if method == "pearson":
        coefficient = dataframe["burned_count"].corr(
            dataframe["health_cases"],
            method="pearson",
        )
    elif method == "spearman":
        coefficient = dataframe["burned_count"].rank().corr(
            dataframe["health_cases"].rank(),
            method="pearson",
        )
    else:
        raise ValueError(f"Unsupported correlation method: {method}")

    return None if pd.isna(coefficient) else float(coefficient)


def _parse_numeric_value(value):
    if value is None:
        return None

    value = str(value).strip()
    if not value or value.lower() in {"nan", "none"}:
        return None

    if value == "-":
        return 0.0

    value = value.replace(".", "").replace(",", ".")

    try:
        return float(value)
    except ValueError:
        return None


def _normalize_federative_unit(value):
    value = "" if value is None else str(value).strip()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(character for character in value if not unicodedata.combining(character))
    return " ".join(value.upper().split())


def _normalize_filter_values(values):
    if not values:
        return None

    return {_normalize_federative_unit(value) for value in values}


def _year_filter(field_name: str, start_year: Optional[int], end_year: Optional[int]):
    filters = {}

    if start_year is not None:
        filters[f"{field_name}__year__gte"] = start_year

    if end_year is not None:
        filters[f"{field_name}__year__lte"] = end_year

    return filters


def get_monthly_burned_dataframe(
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    federative_units: Optional[Iterable[str]] = None,
):
    queryset = (
        Burned.objects.filter(
        **_year_filter("register_at", start_year, end_year)
        )
        .annotate(period=TruncMonth("register_at"))
        .values("period", "federative_unit__name")
        .annotate(burned_count=Count("id"))
        .order_by("period", "federative_unit__name")
    )

    dataframe = pd.DataFrame.from_records(queryset)

    if dataframe.empty:
        return pd.DataFrame(columns=["period", "federative_unit", "burned_count"])

    dataframe["period"] = pd.to_datetime(dataframe["period"])
    dataframe["federative_unit"] = dataframe["federative_unit__name"].map(
        _normalize_federative_unit
    )

    if federative_units:
        dataframe = dataframe[
            dataframe["federative_unit"].isin(_normalize_filter_values(federative_units))
        ]

    return dataframe[["period", "federative_unit", "burned_count"]]


def get_monthly_health_dataframe(
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    federative_units: Optional[Iterable[str]] = None,
    cid_ids: Optional[Iterable[int]] = DEFAULT_CID_IDS,
    type_health_ids: Optional[Iterable[int]] = DEFAULT_TYPE_HEALTH_IDS,
):
    filters = _year_filter("register_at", start_year, end_year)

    if cid_ids:
        filters["cid_id__in"] = cid_ids

    if type_health_ids:
        filters["type_health_id__in"] = type_health_ids

    queryset = DiseaseCase.objects.filter(**filters).values(
        "register_at",
        "federative_unit_name",
        "value",
        "cid_id",
        "type_health_id",
    )

    dataframe = pd.DataFrame.from_records(queryset)

    if dataframe.empty:
        return pd.DataFrame(columns=["period", "federative_unit", "health_cases"])

    dataframe["register_at"] = pd.to_datetime(dataframe["register_at"])
    dataframe["period"] = dataframe["register_at"].dt.to_period("M").dt.to_timestamp()
    dataframe["federative_unit"] = dataframe["federative_unit_name"].map(
        _normalize_federative_unit
    )
    dataframe["health_cases"] = dataframe["value"].map(_parse_numeric_value)

    if federative_units:
        dataframe = dataframe[
            dataframe["federative_unit"].isin(_normalize_filter_values(federative_units))
        ]

    dataframe = dataframe.dropna(subset=["health_cases"])

    return dataframe[
        ["period", "federative_unit", "health_cases", "cid_id", "type_health_id"]
    ]


def build_monthly_correlation_dataframe(
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    federative_units: Optional[Iterable[str]] = None,
    cid_ids: Optional[Iterable[int]] = DEFAULT_CID_IDS,
    type_health_ids: Optional[Iterable[int]] = DEFAULT_TYPE_HEALTH_IDS,
    lag_months: int = 0,
):
    burned = get_monthly_burned_dataframe(
        start_year=start_year,
        end_year=end_year,
        federative_units=federative_units,
    )
    health = get_monthly_health_dataframe(
        start_year=start_year,
        end_year=end_year,
        federative_units=federative_units,
        cid_ids=cid_ids,
        type_health_ids=type_health_ids,
    )

    if lag_months:
        health = health.copy()
        health["period"] = health["period"] - pd.DateOffset(months=lag_months)

    dataframe = burned.merge(
        health,
        on=["period", "federative_unit"],
        how="inner",
    )

    return dataframe.sort_values(["period", "federative_unit"]).reset_index(drop=True)


def run_correlation_tests(
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    federative_units: Optional[Iterable[str]] = None,
    cid_ids: Optional[Iterable[int]] = DEFAULT_CID_IDS,
    type_health_ids: Optional[Iterable[int]] = DEFAULT_TYPE_HEALTH_IDS,
    lag_months: int = 0,
):
    dataframe = build_monthly_correlation_dataframe(
        start_year=start_year,
        end_year=end_year,
        federative_units=federative_units,
        cid_ids=cid_ids,
        type_health_ids=type_health_ids,
        lag_months=lag_months,
    )

    sample_size = len(dataframe)
    results = []

    for method in ("pearson", "spearman"):
        coefficient = None

        if sample_size >= 2:
            coefficient = _correlation_coefficient(dataframe, method)

        results.append(
            CorrelationResult(
                method=method,
                coefficient=coefficient,
                sample_size=sample_size,
                start_year=start_year,
                end_year=end_year,
                lag_months=lag_months,
            )
        )

    return results, dataframe
