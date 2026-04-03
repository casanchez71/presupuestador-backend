import pytest


@pytest.fixture
def sample_items():
    """Flat list of items for tree building tests."""
    return [
        {"id": "a", "parent_id": None, "code": "1", "description": "Seccion 1"},
        {"id": "b", "parent_id": "a", "code": "1.1", "description": "Item 1.1"},
        {"id": "c", "parent_id": "a", "code": "1.2", "description": "Item 1.2"},
        {"id": "d", "parent_id": None, "code": "2", "description": "Seccion 2"},
        {"id": "e", "parent_id": "d", "code": "2.1", "description": "Item 2.1"},
        {"id": "f", "parent_id": "e", "code": "2.1.1", "description": "Sub 2.1.1"},
    ]
