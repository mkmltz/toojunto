from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Callable

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import SessionLocal
from ..groups.service import (
    _numero_ciclo_atual,
    notificar_pendencias_financeiras,
)
from ..models import Grupo


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FinancialNotificationJobResult:
    groups_scanned: int
    groups_processed: int
    groups_skipped: int


def _active_groups(db: Session) -> list[Grupo]:
    return list(
        db.scalars(
            select(Grupo)
            .where(Grupo.status == "ATIVO")
            .order_by(Grupo.id)
        ).all()
    )


def run_financial_notification_job(
    session_factory: Callable[[], Session] = SessionLocal,
) -> FinancialNotificationJobResult:
    """Run existing financial notification rules for every active group."""
    db = session_factory()
    groups_scanned = 0
    groups_processed = 0
    groups_skipped = 0
    try:
        groups = _active_groups(db)
        groups_scanned = len(groups)
        for group in groups:
            cycle_number = _numero_ciclo_atual(group, db)
            if cycle_number > group.quantidade_ciclos:
                groups_skipped += 1
                continue
            try:
                notificar_pendencias_financeiras(group.id, cycle_number, db)
                groups_processed += 1
            except HTTPException as error:
                if error.status_code in (404, 409):
                    db.rollback()
                    groups_skipped += 1
                    continue
                raise
        result = FinancialNotificationJobResult(
            groups_scanned=groups_scanned,
            groups_processed=groups_processed,
            groups_skipped=groups_skipped,
        )
        logger.info(
            "financial_notification_job_completed "
            "groups_scanned=%d groups_processed=%d groups_skipped=%d",
            result.groups_scanned,
            result.groups_processed,
            result.groups_skipped,
        )
        return result
    finally:
        db.close()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        run_financial_notification_job()
    except Exception as error:
        logger.error(
            "financial_notification_job_failed error_type=%s",
            type(error).__name__,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
