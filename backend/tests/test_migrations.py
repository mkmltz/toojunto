from contextlib import nullcontext
import importlib.util
from pathlib import Path
import runpy
from unittest.mock import Mock

from alembic import context
from alembic.config import Config
from alembic.script import ScriptDirectory

from app.config import settings


BACKEND_ROOT = Path(__file__).resolve().parents[1]
ALEMBIC_CONFIG = BACKEND_ROOT / "alembic.ini"
NOTIFICATION_MIGRATION = (
    BACKEND_ROOT
    / "migrations"
    / "versions"
    / "c4a8e2f6b1d3_persistencia_de_notificacoes.py"
)
EMAIL_DELIVERY_MIGRATION = (
    BACKEND_ROOT
    / "migrations"
    / "versions"
    / "e7d3a9c5f2b4_confiabilidade_do_email.py"
)
EXPECTED_TABLES = {
    "ciclos",
    "contemplacoes",
    "convites",
    "entregas_email",
    "grupos",
    "notificacoes",
    "pagamentos",
    "participantes",
    "usuarios",
}


def test_alembic_has_single_head_with_email_delivery_revision():
    config = Config(ALEMBIC_CONFIG)
    scripts = ScriptDirectory.from_config(config)
    revisions = list(scripts.walk_revisions())

    assert Path(scripts.dir).resolve() == BACKEND_ROOT / "migrations"
    assert len(revisions) == 3
    assert revisions[0].revision == "e7d3a9c5f2b4"
    assert revisions[0].down_revision == "c4a8e2f6b1d3"
    assert revisions[0].doc == "confiabilidade do email"
    assert revisions[1].revision == "c4a8e2f6b1d3"
    assert revisions[1].down_revision == "9b2f1c4d7e6a"
    assert revisions[1].doc == "persistencia de notificacoes"
    assert revisions[2].revision == "9b2f1c4d7e6a"
    assert revisions[2].down_revision is None
    assert revisions[2].doc == "baseline MVP 0.1"
    assert scripts.get_heads() == ["e7d3a9c5f2b4"]


def test_alembic_env_uses_application_database_url_and_metadata(monkeypatch):
    configure = Mock()
    monkeypatch.setattr(
        context, "config", Config(ALEMBIC_CONFIG), raising=False
    )
    monkeypatch.setattr(context, "is_offline_mode", lambda: True)
    monkeypatch.setattr(context, "configure", configure)
    monkeypatch.setattr(context, "begin_transaction", nullcontext)
    monkeypatch.setattr(context, "run_migrations", Mock())

    namespace = runpy.run_path(str(BACKEND_ROOT / "migrations" / "env.py"))

    metadata = namespace["target_metadata"]
    assert set(metadata.tables) == EXPECTED_TABLES
    assert configure.call_args.kwargs["url"] == settings.database_url
    assert configure.call_args.kwargs["target_metadata"] is metadata


def test_notification_migration_upgrade_and_downgrade_are_symmetric():
    spec = importlib.util.spec_from_file_location(
        "notification_migration", NOTIFICATION_MIGRATION
    )
    assert spec is not None and spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    migration.op = Mock()
    migration.op.f.side_effect = lambda name: name

    migration.upgrade()

    migration.op.create_table.assert_called_once()
    assert migration.op.create_table.call_args.args[0] == "notificacoes"
    migration.op.create_index.assert_called_once_with(
        "ix_notificacoes_usuario_id",
        "notificacoes",
        ["usuario_id"],
        unique=False,
    )

    migration.op.reset_mock()
    migration.op.f.side_effect = lambda name: name
    migration.downgrade()

    migration.op.drop_index.assert_called_once_with(
        "ix_notificacoes_usuario_id", table_name="notificacoes"
    )
    migration.op.drop_table.assert_called_once_with("notificacoes")


def test_email_delivery_migration_upgrade_and_downgrade_are_symmetric():
    spec = importlib.util.spec_from_file_location(
        "email_delivery_migration", EMAIL_DELIVERY_MIGRATION
    )
    assert spec is not None and spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    migration.op = Mock()
    migration.op.f.side_effect = lambda name: name

    migration.upgrade()

    migration.op.create_table.assert_called_once()
    assert migration.op.create_table.call_args.args[0] == "entregas_email"
    migration.op.create_index.assert_called_once_with(
        "ix_entregas_email_notificacao_id",
        "entregas_email",
        ["notificacao_id"],
        unique=False,
    )

    migration.op.reset_mock()
    migration.op.f.side_effect = lambda name: name
    migration.downgrade()

    migration.op.drop_index.assert_called_once_with(
        "ix_entregas_email_notificacao_id", table_name="entregas_email"
    )
    migration.op.drop_table.assert_called_once_with("entregas_email")
