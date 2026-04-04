"""Tests for Excel parser: date-code normalization and multi-format support."""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import pytest

from app.tree import normalize_date_code, normalize_item_code


class TestNormalizeDateCode:
    """Test date-encoded item code conversion."""

    def test_timestamp_basic(self):
        """2025-01-01 -> section 1, item 1 -> '1.1'"""
        assert normalize_date_code(pd.Timestamp("2025-01-01")) == "1.1"

    def test_timestamp_section_2(self):
        """2025-01-02 -> section 2, item 1 -> '2.1'"""
        assert normalize_date_code(pd.Timestamp("2025-01-02")) == "2.1"

    def test_timestamp_item_12(self):
        """2025-12-02 -> section 2, item 12 -> '2.12'"""
        assert normalize_date_code(pd.Timestamp("2025-12-02")) == "2.12"

    def test_timestamp_month_2(self):
        """2025-02-01 -> section 1, item 2 -> '1.2'"""
        assert normalize_date_code(pd.Timestamp("2025-02-01")) == "1.2"

    def test_datetime_object(self):
        """Standard datetime also works."""
        assert normalize_date_code(datetime(2025, 3, 4)) == "4.3"

    def test_date_string(self):
        """String in YYYY-MM-DD format."""
        assert normalize_date_code("2025-01-01") == "1.1"

    def test_date_string_with_time(self):
        """String with time component."""
        assert normalize_date_code("2025-02-01 00:00:00") == "1.2"

    def test_not_a_date(self):
        """Non-date values return None."""
        assert normalize_date_code("1.1") is None
        assert normalize_date_code(42) is None
        assert normalize_date_code(None) is None

    def test_normal_code_passthrough(self):
        """Normal codes are not misidentified as dates."""
        assert normalize_date_code("OBRADOR") is None
        assert normalize_date_code("0.8") is None


class TestNormalizeItemCodeDates:
    """Test that normalize_item_code handles Timestamps from Excel."""

    def test_timestamp_converted(self):
        assert normalize_item_code(pd.Timestamp("2025-01-01")) == "1.1"

    def test_timestamp_section_2(self):
        assert normalize_item_code(pd.Timestamp("2025-01-02")) == "2.1"

    def test_normal_code_unchanged(self):
        assert normalize_item_code("0.8") == "0.8"

    def test_dash_format(self):
        """Lugones X.Y-Z format: '3.0-1' -> '3.0.1'"""
        assert normalize_item_code("3.0-1") == "3.0.1"

    def test_dash_format_2(self):
        assert normalize_item_code("4.1-7") == "4.1.7"

    def test_normal_code_with_dash_text(self):
        """Dashes followed by text: regex converts digit-dash-digit only."""
        # "3-ESTRUCTURA" -> "3-ESTRUCTURA" (dash stays because E is not a digit)
        result = normalize_item_code("3-ESTRUCTURA")
        assert "3" in result  # The section number is preserved

    def test_passthrough_numeric(self):
        assert normalize_item_code("2.14") == "2.14"

    def test_none(self):
        assert normalize_item_code(None) == ""

    def test_nan(self):
        assert normalize_item_code(float("nan")) == ""


class TestDateCodeEdgeCases:
    """Edge cases for the date-code mapping across Lugones and El Encuentro."""

    def test_lugones_item_1_1(self):
        """Lugones: 2025-01-01 = first item, first section."""
        assert normalize_item_code(pd.Timestamp("2025-01-01")) == "1.1"

    def test_encuentro_item_1_1(self):
        """El Encuentro: 2024-01-01 = same mapping regardless of year."""
        assert normalize_item_code(pd.Timestamp("2024-01-01")) == "1.1"

    def test_encuentro_movimiento_tierras(self):
        """El Encuentro section 2 items: 2024-01-02 = 2.1, 2024-02-02 = 2.2, 2024-03-02 = 2.3"""
        assert normalize_item_code(pd.Timestamp("2024-01-02")) == "2.1"
        assert normalize_item_code(pd.Timestamp("2024-02-02")) == "2.2"
        assert normalize_item_code(pd.Timestamp("2024-03-02")) == "2.3"
