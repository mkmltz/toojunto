from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from scripts import postgres_backup


def test_timestamped_backup_name_uses_utc():
    instant = datetime(2026, 9, 28, 15, 4, 5, tzinfo=timezone.utc)

    assert (
        postgres_backup._timestamped_name(instant)
        == "toojunto_20260928_150405_utc.dump"
    )


def test_restore_requires_exact_target_confirmation(monkeypatch):
    run = Mock()
    monkeypatch.setattr(postgres_backup, "_run", run)

    with pytest.raises(postgres_backup.BackupError, match="confirmation"):
        postgres_backup.restore_backup(
            Path("compose.yml"),
            Path("environment.env"),
            "toojunto",
            Path("valid.dump"),
            "restored_database",
            "different_database",
        )

    run.assert_not_called()


def test_restore_rejects_missing_backup_before_running_docker(monkeypatch):
    run = Mock()
    monkeypatch.setattr(postgres_backup, "_run", run)

    with pytest.raises(postgres_backup.BackupError, match="not found"):
        postgres_backup.restore_backup(
            Path("compose.yml"),
            Path("environment.env"),
            "toojunto",
            Path("missing.dump"),
            "restored_database",
            "restored_database",
        )

    run.assert_not_called()


def test_restore_rejects_primary_database(monkeypatch):
    monkeypatch.setattr(Path, "is_file", lambda unused: True)
    monkeypatch.setattr(Path, "stat", lambda unused: SimpleNamespace(st_size=10))
    monkeypatch.setattr(postgres_backup, "_primary_database", lambda unused: "primary")
    query = Mock()
    monkeypatch.setattr(postgres_backup, "_query_target", query)

    with pytest.raises(postgres_backup.BackupError, match="Refusing"):
        postgres_backup.restore_backup(
            Path("compose.yml"),
            Path("environment.env"),
            "toojunto",
            Path("valid.dump"),
            "primary",
            "primary",
        )

    query.assert_not_called()
