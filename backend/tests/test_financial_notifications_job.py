from unittest.mock import Mock

import pytest

from app.jobs import financial_notifications


def test_job_sem_grupos_elegiveis_fecha_sessao_e_retorna_resultado():
    db = Mock()
    db.scalars.return_value.all.return_value = []

    result = financial_notifications.run_financial_notification_job(
        session_factory=lambda: db,
    )

    assert result.groups_scanned == 0
    assert result.groups_processed == 0
    assert result.groups_skipped == 0
    db.close.assert_called_once_with()


def test_job_fecha_sessao_e_propaga_falha_operacional(monkeypatch):
    db = Mock()
    monkeypatch.setattr(
        financial_notifications,
        "_active_groups",
        Mock(side_effect=RuntimeError("falha controlada")),
    )

    with pytest.raises(RuntimeError, match="falha controlada"):
        financial_notifications.run_financial_notification_job(
            session_factory=lambda: db,
        )

    db.close.assert_called_once_with()


def test_main_retorna_exit_code_zero_em_execucao_normal(monkeypatch):
    monkeypatch.setattr(
        financial_notifications,
        "run_financial_notification_job",
        Mock(return_value=financial_notifications.FinancialNotificationJobResult(0, 0, 0)),
    )

    assert financial_notifications.main() == 0


def test_main_retorna_exit_code_um_sem_logar_detalhe_da_excecao(
    monkeypatch,
    caplog,
):
    monkeypatch.setattr(
        financial_notifications,
        "run_financial_notification_job",
        Mock(side_effect=RuntimeError("conteudo financeiro sensivel")),
    )

    assert financial_notifications.main() == 1
    assert "RuntimeError" in caplog.text
    assert "conteudo financeiro sensivel" not in caplog.text
