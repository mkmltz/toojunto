"""Safely adopt an existing MVP 0.1 PostgreSQL schema into Alembic."""

from pathlib import Path
import sys

from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Connection
from sqlalchemy.pool import NullPool

from . import models  # noqa: F401
from .config import settings
from .db import Base


BASELINE_REVISION = "9b2f1c4d7e6a"
BACKEND_ROOT = Path(__file__).resolve().parents[1]
ALEMBIC_CONFIG = BACKEND_ROOT / "alembic.ini"


class AdoptionError(RuntimeError):
    """Raised when a database cannot safely adopt the MVP 0.1 baseline."""


def _load_revision_graph() -> ScriptDirectory:
    config = Config(ALEMBIC_CONFIG)
    scripts = ScriptDirectory.from_config(config)
    baseline = scripts.get_revision(BASELINE_REVISION)
    if baseline is None or baseline.down_revision is not None:
        raise AdoptionError(
            f"Revision {BASELINE_REVISION} is not the Alembic baseline"
        )
    if scripts.get_heads() != [BASELINE_REVISION]:
        raise AdoptionError(
            f"Revision {BASELINE_REVISION} is not the single Alembic head"
        )
    return scripts


def _validate_legacy_schema(connection: Connection) -> MigrationContext:
    if connection.dialect.name != "postgresql":
        raise AdoptionError("MVP 0.1 adoption requires PostgreSQL")

    inspector = inspect(connection)
    if inspector.has_table("alembic_version"):
        raise AdoptionError(
            "Database already has alembic_version; adoption was not performed"
        )

    expected_tables = set(Base.metadata.tables)
    actual_tables = set(inspector.get_table_names())
    if actual_tables != expected_tables:
        missing = sorted(expected_tables - actual_tables)
        unexpected = sorted(actual_tables - expected_tables)
        raise AdoptionError(
            "Application table set differs from MVP 0.1 "
            f"(missing={missing}, unexpected={unexpected})"
        )

    # Blocks concurrent DDL while preserving ordinary reads and writes.
    quoted_tables = ", ".join(
        inspector.dialect.identifier_preparer.quote(table_name)
        for table_name in sorted(expected_tables)
    )
    connection.execute(
        text(f"LOCK TABLE {quoted_tables} IN ACCESS SHARE MODE")
    )

    migration_context = MigrationContext.configure(
        connection,
        opts={"compare_type": True},
    )
    differences = compare_metadata(migration_context, Base.metadata)
    if differences:
        details = "\n".join(f"- {difference!r}" for difference in differences)
        raise AdoptionError(
            "Database schema differs from the MVP 0.1 baseline; "
            f"stamp was not performed:\n{details}"
        )
    return migration_context


def adopt_mvp_0_1() -> None:
    """Validate a legacy database and atomically stamp the fixed baseline."""
    scripts = _load_revision_graph()
    engine = create_engine(settings.database_url, poolclass=NullPool)
    try:
        with engine.begin() as connection:
            migration_context = _validate_legacy_schema(connection)
            migration_context.stamp(scripts, BASELINE_REVISION)
    finally:
        engine.dispose()


def main() -> int:
    try:
        adopt_mvp_0_1()
    except AdoptionError as error:
        print(f"ABORTED: {error}", file=sys.stderr)
        return 1
    print(f"Database adopted at Alembic revision {BASELINE_REVISION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
