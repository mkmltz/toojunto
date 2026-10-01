from unittest.mock import Mock

import pytest

from app import adopt_mvp_0_1


def test_revision_graph_requires_single_head_descending_from_fixed_baseline():
    scripts = adopt_mvp_0_1._load_revision_graph()

    assert scripts.get_heads() == ["a8c3e1f5b7d9"]
    revisions = scripts.iterate_revisions("a8c3e1f5b7d9", "base")
    assert adopt_mvp_0_1.BASELINE_REVISION in {
        revision.revision for revision in revisions
    }
    assert scripts.get_revision(adopt_mvp_0_1.BASELINE_REVISION).down_revision is None


def test_incompatible_schema_aborts_before_stamp(monkeypatch):
    connection = Mock()
    connection.dialect.name = "postgresql"
    inspector = Mock()
    inspector.has_table.return_value = False
    inspector.get_table_names.return_value = ["usuarios"]
    monkeypatch.setattr(adopt_mvp_0_1, "inspect", lambda unused: inspector)
    configure = Mock()
    monkeypatch.setattr(adopt_mvp_0_1.MigrationContext, "configure", configure)

    with pytest.raises(adopt_mvp_0_1.AdoptionError, match="table set differs"):
        adopt_mvp_0_1._validate_legacy_schema(connection)

    configure.assert_not_called()
    connection.execute.assert_not_called()


def test_existing_alembic_history_aborts_before_schema_comparison(monkeypatch):
    connection = Mock()
    connection.dialect.name = "postgresql"
    inspector = Mock()
    inspector.has_table.return_value = True
    monkeypatch.setattr(adopt_mvp_0_1, "inspect", lambda unused: inspector)
    compare = Mock()
    monkeypatch.setattr(adopt_mvp_0_1, "compare_metadata", compare)

    with pytest.raises(adopt_mvp_0_1.AdoptionError, match="already has alembic_version"):
        adopt_mvp_0_1._validate_legacy_schema(connection)

    compare.assert_not_called()
