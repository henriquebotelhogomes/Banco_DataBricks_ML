# Banco_DataBricks_ML — Sistema de Avaliação de Risco de Crédito com IA

[![CI](https://github.com/henriquebotelhogomes/Banco_DataBricks_ML/actions/workflows/ci.yml/badge.svg)](https://github.com/henriquebotelhogomes/Banco_DataBricks_ML/actions/workflows/ci.yml)

Projeto demo de **Engenharia de IA e MLOps** para o segmento financeiro: previsão de probabilidade de inadimplência (*default*) com explicabilidade regulatória (SHAP), construído sobre **Databricks + GCP**.

## 🏗️ Arquitetura

```
Kaggle (Home Credit) ──► GCS (Bronze) ──► Databricks PySpark (Bronze→Silver→Gold / Delta Lake)
                                                  │
                                                  ▼
                              MLflow (Tracking + Model Registry) ── XGBoost
                                                  │  promoção a Production
                                                  ▼
                              GCS (model.bst) ──► FastAPI @ Cloud Run ──► Swagger UI
                                                  │  log de predições (BigQuery)
                                                  ▼
                              Evidently AI (Databricks Job semanal) ──► alertas Pub/Sub
```

## 🛠️ Stack

| Camada | Tecnologia |
| :--- | :--- |
| Linguagem / deps | Python 3.11 + **uv** (`pyproject.toml` + `uv.lock`) |
| Engenharia de dados | Databricks (PySpark, Delta Lake, Workflows) |
| ML | XGBoost + SHAP |
| MLOps | MLflow (Registry) · DVC (dados) · Evidently AI (drift) |
| API | FastAPI + Pydantic v2 |
| Cloud | GCP (Cloud Run, BigQuery, GCS, Artifact Registry, Pub/Sub) |
| IaC / CI-CD | Terraform · GitHub Actions |

## 🚀 Como rodar localmente

```bash
git clone https://github.com/henriquebotelhogomes/Banco_DataBricks_ML.git
cd Banco_DataBricks_ML
uv sync                                # cria .venv e instala dependências
uv run uvicorn src.api.main:app --reload
# Swagger UI: http://localhost:8000/docs
```

### Testes

```bash
uv run pytest
```

### Docker

```bash
docker build -t credit-risk-api:dev .
docker run --rm -p 8080:8080 credit-risk-api:dev
# http://localhost:8080/health
```

## 📡 API

| Endpoint | Método | Descrição |
| :--- | :--- | :--- |
| `/health` | GET | Health check |
| `/predict` | POST | Probabilidade de default + decisão + explicação SHAP |
| `/docs` | GET | Swagger UI (interface de demonstração) |

Exemplo de requisição:

```json
{
  "client_id": "12345",
  "income": 5000.0,
  "age": 30,
  "avg_spend_90d": 1250.5,
  "total_late_payments": 0,
  "current_bureau_score": 0.72
}
```

## 📚 Documentação

- [PRD.md](./PRD.md) — plano de implementação com checklists de progresso
- [FinTech Solutions S.A.md](./FinTech%20Solutions%20S.A.md) — especificação técnica completa

## 📌 Status

**Fase 0 concluída** — API esqueleto (stub de inferência), testes, CI e Docker.
Próximas fases: GCP (infra real) → Databricks (pipeline + modelo) → deploy Cloud Run + monitoramento de drift. Acompanhe em [PRD.md](./PRD.md).
