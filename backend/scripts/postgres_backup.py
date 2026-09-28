"""Create and restore PostgreSQL custom-format backups through Docker Compose."""

import argparse
from datetime import datetime, timezone
from pathlib import Path
import re
import subprocess
import sys
from typing import BinaryIO, Sequence


DATABASE_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$")


class BackupError(RuntimeError):
    """Raised when a backup or restore safety check fails."""


def _compose_command(
    compose_file: Path, env_file: Path, project_name: str
) -> list[str]:
    if not compose_file.is_file():
        raise BackupError(f"Compose file not found: {compose_file}")
    if not env_file.is_file():
        raise BackupError(f"Environment file not found: {env_file}")
    if not DATABASE_NAME.fullmatch(project_name):
        raise BackupError("Compose project name contains unsupported characters")
    return [
        "docker",
        "compose",
        "--project-name",
        project_name,
        "--env-file",
        str(env_file),
        "-f",
        str(compose_file),
    ]


def _run(
    command: Sequence[str],
    *,
    stdin: BinaryIO | None = None,
    stdout: BinaryIO | int = subprocess.PIPE,
) -> subprocess.CompletedProcess[bytes]:
    try:
        result = subprocess.run(
            command,
            stdin=stdin,
            stdout=stdout,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as error:
        raise BackupError(f"Could not execute {command[0]}: {error}") from error
    if result.returncode != 0:
        detail = result.stderr.decode(errors="replace").strip()
        raise BackupError(
            f"Command failed with exit code {result.returncode}"
            + (f": {detail}" if detail else "")
        )
    return result


def _timestamped_name(now: datetime | None = None) -> str:
    instant = now or datetime.now(timezone.utc)
    return f"toojunto_{instant.astimezone(timezone.utc):%Y%m%d_%H%M%S}_utc.dump"


def _database_name(value: str) -> str:
    if not DATABASE_NAME.fullmatch(value):
        raise BackupError(
            "Target database must use only letters, numbers, underscores or hyphens"
        )
    return value


def create_backup(
    compose_file: Path,
    env_file: Path,
    project_name: str,
    output_dir: Path,
    filename: str | None = None,
) -> Path:
    compose = _compose_command(compose_file, env_file, project_name)
    output_dir.mkdir(parents=True, exist_ok=True)
    backup_name = filename or _timestamped_name()
    if Path(backup_name).name != backup_name:
        raise BackupError("Backup filename must not contain a directory")
    destination = output_dir / backup_name
    if destination.suffix != ".dump":
        raise BackupError("Backup filename must end with .dump")
    if destination.exists():
        raise BackupError(f"Backup already exists: {destination}")

    temporary = destination.with_suffix(destination.suffix + ".tmp")
    temporary.unlink(missing_ok=True)
    dump_command = compose + [
        "exec",
        "-T",
        "db",
        "sh",
        "-c",
        'exec pg_dump --format=custom --username="$POSTGRES_USER" '
        '--dbname="$POSTGRES_DB"',
    ]
    try:
        with temporary.open("wb") as output:
            _run(dump_command, stdout=output)
        if temporary.stat().st_size == 0:
            raise BackupError("pg_dump produced an empty backup")
        with temporary.open("rb") as dump:
            _run(
                compose
                + ["exec", "-T", "db", "pg_restore", "--list"],
                stdin=dump,
            )
        temporary.replace(destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return destination


def _primary_database(compose: Sequence[str]) -> str:
    result = _run(
        list(compose)
        + ["exec", "-T", "db", "sh", "-c", 'printf %s "$POSTGRES_DB"']
    )
    database = result.stdout.decode().strip()
    if not database:
        raise BackupError("POSTGRES_DB is empty in the database service")
    return database


def _query_target(compose: Sequence[str], target: str, query: str) -> str:
    result = _run(
        list(compose)
        + [
            "exec",
            "-T",
            "-e",
            f"TARGET_DB={target}",
            "-e",
            f"BACKUP_QUERY={query}",
            "db",
            "sh",
            "-c",
            'exec psql --username="$POSTGRES_USER" --dbname="$TARGET_DB" '
            '--tuples-only --no-align --command="$BACKUP_QUERY"',
        ]
    )
    return result.stdout.decode().strip()


def restore_backup(
    compose_file: Path,
    env_file: Path,
    project_name: str,
    backup_file: Path,
    target_database: str,
    confirmation: str,
) -> None:
    target = _database_name(target_database)
    if confirmation != target:
        raise BackupError("Target confirmation does not match --target-db")
    if not backup_file.is_file():
        raise BackupError(f"Backup file not found: {backup_file}")
    if backup_file.stat().st_size == 0:
        raise BackupError(f"Backup file is empty: {backup_file}")

    compose = _compose_command(compose_file, env_file, project_name)
    primary = _primary_database(compose)
    if target == primary:
        raise BackupError(
            "Refusing to restore over POSTGRES_DB; use a distinct, empty target database"
        )

    relation_count = _query_target(
        compose,
        target,
        "SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace "
        "WHERE n.nspname NOT IN ('pg_catalog','information_schema') "
        "AND n.nspname NOT LIKE 'pg_toast%' AND c.relkind IN ('r','p','v','m','S');",
    )
    if relation_count != "0":
        raise BackupError(
            f"Target database is not empty (user relations={relation_count})"
        )

    restore_command = list(compose) + [
        "exec",
        "-T",
        "-e",
        f"TARGET_DB={target}",
        "db",
        "sh",
        "-c",
        'exec pg_restore --exit-on-error --single-transaction --no-owner '
        '--no-privileges --username="$POSTGRES_USER" --dbname="$TARGET_DB"',
    ]
    with backup_file.open("rb") as dump:
        _run(restore_command, stdin=dump)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compose-file", required=True, type=Path)
    parser.add_argument("--env-file", required=True, type=Path)
    parser.add_argument("--project-name", required=True)
    commands = parser.add_subparsers(dest="operation", required=True)

    backup = commands.add_parser("backup")
    backup.add_argument("--output-dir", required=True, type=Path)
    backup.add_argument("--filename")

    restore = commands.add_parser("restore")
    restore.add_argument("--backup-file", required=True, type=Path)
    restore.add_argument("--target-db", required=True)
    restore.add_argument("--confirm-target-db", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.operation == "backup":
            backup = create_backup(
                args.compose_file,
                args.env_file,
                args.project_name,
                args.output_dir,
                args.filename,
            )
            print(f"Backup completed: {backup} ({backup.stat().st_size} bytes)")
        else:
            restore_backup(
                args.compose_file,
                args.env_file,
                args.project_name,
                args.backup_file,
                args.target_db,
                args.confirm_target_db,
            )
            print(f"Restore completed into database: {args.target_db}")
    except BackupError as error:
        print(f"ABORTED: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
