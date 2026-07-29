"""Credit Risk Scoring API — ponto de entrada FastAPI.

Única interface do sistema (sem frontend dedicado): demonstração via
Swagger UI (/docs) e ReDoc (/redoc). Ver especificação técnica, seção 10.
"""

import pandas as pd
from fastapi import BackgroundTasks, FastAPI, HTTPException

from src.api.schemas import CreditRequest, CreditResponse
from src.api.services.inference import (
    DECISION_THRESHOLD,
    get_top_shap_features,
    predict_default_probability,
)
from src.api.services.logging_bq import log_prediction_bq

app = FastAPI(
    title="Credit Risk Scoring API",
    description=(
        "API de avaliação de risco de crédito com IA (XGBoost + SHAP). "
        "Projeto demo: Databricks + GCP + MLOps."
    ),
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict:
    return {"status": "healthy"}


@app.post("/predict", response_model=CreditResponse)
async def predict_risk(
    request: CreditRequest, background_tasks: BackgroundTasks
) -> CreditResponse:
    try:
        input_data = pd.DataFrame([request.model_dump()])
        features = input_data.drop(columns=["client_id"])

        risk_score = predict_default_probability(features)
        top_features = get_top_shap_features(features, n=3)

        # Log assíncrono (insumo do monitoramento de drift — Fase 3)
        background_tasks.add_task(log_prediction_bq, request.model_dump(), risk_score)

        return CreditResponse(
            client_id=request.client_id,
            probability_of_default=risk_score,
            decision="APPROVED" if risk_score < DECISION_THRESHOLD else "REJECTED",
            explanation=top_features,
        )
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e))
