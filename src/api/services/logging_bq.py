"""Logging assíncrono de predições no BigQuery.

FASE 0: implementação stub — apenas loga em stdout (Cloud Logging capta em produção).
FASE 3: gravar na tabela BigQuery `credit_risk_features.prediction_logs`,
insumo do job semanal de drift (Evidently AI).
"""

import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger("prediction_logs")


def log_prediction_bq(payload: dict, risk_score: float) -> None:
    """Stub (Fase 0): registra a predição em log estruturado.

    Na Fase 3 será substituído por insert na tabela
    `credit_risk_features.prediction_logs` via google-cloud-bigquery.
    """
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "probability_of_default": risk_score,
        **payload,
    }
    logger.info(json.dumps(record, default=str))
