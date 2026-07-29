"""Schemas Pydantic (v2) da Credit Risk Scoring API.

O contrato de entrada espelha exatamente o schema da tabela Gold
(`gold_credit_features`) gerada no Databricks — paridade treino/serving.
"""

from pydantic import BaseModel, Field


class CreditRequest(BaseModel):
    """Payload de solicitação de análise de crédito."""

    client_id: str
    income: float = Field(..., gt=0, description="Renda total anual (AMT_INCOME_TOTAL)")
    age: int = Field(..., ge=18, description="Idade em anos (derivada de DAYS_BIRTH)")
    avg_spend_90d: float = Field(
        ..., ge=0, description="Gasto médio de cartão nos últimos 90 dias (AMT_BALANCE)"
    )
    total_late_payments: int = Field(
        ..., ge=0, description="Total de parcelas pagas com mais de 30 dias de atraso"
    )
    current_bureau_score: float = Field(
        ..., ge=0, le=1, description="Média de EXT_SOURCE_1/2/3 (proxy de score de bureau)"
    )


class FeatureImpact(BaseModel):
    """Contribuição SHAP de uma feature para a decisão."""

    feature: str
    impact: float


class CreditResponse(BaseModel):
    """Resposta da análise de crédito."""

    client_id: str
    probability_of_default: float = Field(..., ge=0, le=1)
    decision: str = Field(..., description="APPROVED ou REJECTED")
    explanation: list[FeatureImpact] = Field(
        default_factory=list, description="Top features SHAP que justificam a decisão"
    )
