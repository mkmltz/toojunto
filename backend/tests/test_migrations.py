from contextlib import nullcontext
from pathlib import Path
import runpy
from unittest.mock import Mock

from alembic import context
from alembic.config import Config
from alembic.script import ScriptDirectory

from app.config import settings


BACKEND_ROOT = Path(__file__).resolve().parents[1]
ALEMBIC_CONFIG = BACKEND_ROOT / "alembic.ini"
EXPECTED_TABLES = {
    "ciclos",
    "contemplacoes",
    "convites",
    "grupos",
    "pagamentos",
    "participantes",
    "usuarios",
}


def test_alembic_configuration_loads_without_revisions():
    config = Config(ALEMBIC_CONFIG)
    scripts = ScriptDirectory.from_config(config)

    assert Path(scripts.dir).resolve() == BACKEND_ROOT / "migrations"
    assert list(scripts.walk_revisions()) == []


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
