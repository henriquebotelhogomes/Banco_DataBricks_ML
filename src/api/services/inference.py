"""Serviço de inferência.

FASE 0: implementação stub — score simulado por heurística determinística.
FASE 3: substituir por carregamento do modelo XGBoost real a partir de
`gs://fintech-models-bucket/v1/model.bst` no startup (lifespan) + SHAP.
"""

import pandas as pd

# Threshold de negócio: probabilidade de default acima disso => REJECTED
DECISION_THRESHOLD = 0.3


def predict_default_probability(features: pd.DataFrame) -> float:
    """Stub de inferência (Fase 0).

    Heurística simples e determinística apenas para viabilizar o contrato
    da API e os testes antes do modelo real (Fase 2/3):
    score de bureau alto e sem atrasos => risco baixo.
    """
    row = features.iloc[0]
    risk = 1.0 - float(row["current_bureau_score"])
    risk += min(int(row["total_late_payments"]), 10) * 0.05
    return round(min(max(risk * 0.5, 0.0), 1.0), 4)


def get_top_shap_features(features: pd.DataFrame, n: int = 3) -> list[dict]:
    """Stub de explicabilidade (Fase 0).

    Na Fase 3 será substituído por SHAP values reais do modelo carregado.
    """
    _ = features
    return [
        {"feature": "current_bureau_score", "impact": -0.18},
        {"feature": "total_late_payments", "impact": 0.12},
        {"feature": "income", "impact": -0.05},
    ][:n]
