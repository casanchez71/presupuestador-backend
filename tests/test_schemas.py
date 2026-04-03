from uuid import UUID

import pytest
from pydantic import ValidationError

from app.schemas import (
    AnalysisResponse,
    BudgetCreate,
    BudgetItemCreate,
    BudgetItemUpdate,
)


class TestBudgetCreate:
    def test_minimal(self):
        b = BudgetCreate(name="Test")
        assert b.name == "Test"
        assert b.description is None

    def test_with_description(self):
        b = BudgetCreate(name="Test", description="Desc")
        assert b.description == "Desc"

    def test_name_required(self):
        with pytest.raises(ValidationError):
            BudgetCreate()


class TestBudgetItemCreate:
    def test_minimal(self):
        item = BudgetItemCreate(description="Columnas")
        assert item.description == "Columnas"
        assert item.cantidad is None
        assert item.mat_unitario is None

    def test_full(self):
        item = BudgetItemCreate(
            code="1.1",
            description="Columnas H30",
            unidad="m3",
            cantidad=23,
            mat_unitario=548114,
            mo_unitario=600000,
            mat_total=12606630,
            mo_total=13785000,
        )
        assert item.cantidad == 23


class TestBudgetItemUpdate:
    def test_partial(self):
        upd = BudgetItemUpdate(cantidad=50)
        data = upd.model_dump(exclude_unset=True)
        assert data == {"cantidad": 50}


class TestAnalysisResponse:
    def test_valid(self):
        r = AnalysisResponse(
            budget_id="abc",
            mat_total=100,
            mo_total=200,
            directo_total=300,
            indirecto_total=42,
            beneficio_total=75,
            neto_total=417,
            items_count=10,
        )
        assert r.neto_total == 417
