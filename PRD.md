# PRD — Sistema de Avaliação de Risco de Crédito com IA

**Product Requirements Document / Plano de Implementação com Checklists**

| Campo | Valor |
| :--- | :--- |
| **Projeto** | Sistema de Avaliação de Risco de Crédito com IA (FinTech Solutions S.A.) |
| **Repositório** | [github.com/henriquebotelhogomes/Banco_DataBricks_ML](https://github.com/henriquebotelhogomes/Banco_DataBricks_ML) — **público** |
| **Documento base** | [FinTech Solutions S.A.md](./FinTech%20Solutions%20S.A.md) (especificação técnica) |
| **Objetivo** | Projeto demo para demonstrar as competências da vaga em [descricao_vaga.md](./descricao_vaga.md) |
| **Status geral** | 🟡 Em andamento — Fase 0 |
| **Última atualização** | 29/07/2026 |

**Legenda de status:** `[ ]` pendente · `[x]` concluído · ⏳ em andamento · 🚫 bloqueado

> ⚠️ **Repositório PÚBLICO**: nunca commitar `gcp-key.json`, `.env`, tokens Databricks/Kaggle ou qualquer credencial. O `.gitignore` deve ser o **primeiro arquivo** do repositório.

---

## 1. Visão Geral do Produto

### 1.1. Problema
Substituir análise de crédito manual/estatística tradicional por um modelo de ML que prevê a probabilidade de inadimplência (*default*), com decisão em segundos e explicabilidade regulatória.

### 1.2. Solução
Pipeline completo de ML em produção: dados do **Home Credit Default Risk** (Kaggle) → engenharia de dados no **Databricks** (PySpark/Delta) → treinamento **XGBoost** com **MLflow** → API REST **FastAPI** no **Cloud Run** (GCP) → monitoramento de drift com **Evidently AI** → tudo automatizado com **GitHub Actions** e **Terraform**.

### 1.3. Competências demonstradas (rastreabilidade com a vaga)

| Requisito da vaga | Onde é demonstrado |
| :--- | :--- |
| IA/ML | XGBoost + SHAP (Fases 2 e 3) |
| Python para pipelines e modelos | Todo o projeto |
| GCP | Storage, BigQuery, Cloud Run, Cloud Build, Artifact Registry, Pub/Sub, IAM (Fases 1 e 3) |
| Databricks e engenharia de dados | PySpark, Delta Lake, Workflows (Fase 2) |
| MLOps, versionamento e monitoramento | MLflow, DVC, Evidently AI (Fases 2 e 3) |
| APIs REST e integração de IA | FastAPI + Swagger (Fases 0 e 3) |
| Git, CI/CD e boas práticas | GitHub Actions, Terraform, testes (Fases 0, 1 e 3) |
| Metodologias ágeis | Este PRD com sprints/checklists e DoD |

### 1.4. Métricas de sucesso
- **ML:** AUC-ROC > 0.85 · KS > 40
- **Negócio:** decisão de crédito em < 5 segundos
- **Engenharia:** latência de inferência < 200ms · disponibilidade 99.9%

---

## 2. Estrutura do Repositório (alvo)

A estrutura da seção 6 da especificação, adaptada para a raiz do repositório `Banco_DataBricks_ML`:

```text
Banco_DataBricks_ML/
├── .github/workflows/      # CI/CD (GitHub Actions)
├── data/raw/               # CSVs do Home Credit (via DVC, fora do Git)
├── infra/terraform/        # Recursos GCP (IaC)
├── notebooks/databricks/   # Notebooks PySpark (ETL Bronze→Gold)
├── src/
│   ├── data/               # Ingestão e processamento
│   ├── models/             # Treinamento e validação
│   ├── api/                # API FastAPI (main.py, schemas.py, services/)
│   └── utils/              # Auxiliares e logging
├── tests/                  # Testes unitários e integração
├── Dockerfile
├── dvc.yaml
├── ml_pipeline.py          # Orquestração dos Databricks Jobs
├── pyproject.toml          # Dependências e metadados (gerenciados com uv)
├── uv.lock                 # Lockfile determinístico (uv)
├── PRD.md                  # Este documento
├── FinTech Solutions S.A.md
└── descricao_vaga.md
```

---

## 3. FASE 0 — Fundação Local (custo zero) 🟡 EM ANDAMENTO

> **Objetivo:** repositório funcional com API esqueleto, testes e CI verde — sem gastar créditos nem ativar trials.

### 3.1. Repositório e Git
- [ ] Criar `.gitignore` (`.venv/`, `.env`, `gcp-key.json`, `data/`, `__pycache__`, `*.bst`, `.dvc/cache`)
- [ ] Inicializar Git local e conectar ao remote `https://github.com/henriquebotelhogomes/Banco_DataBricks_ML`
- [ ] Criar `README.md` com visão geral, arquitetura e badge de CI
- [ ] Commit inicial com PRD + especificação + descrição da vaga
- [ ] Criar estrutura de pastas (seção 2 deste PRD)

### 3.2. Ambiente local (spec 1.4) — gerenciado com **uv**
- [ ] Python 3.11+ instalado e verificado (`python --version`)
- [ ] Docker Desktop instalado e verificado (`docker --version`)
- [ ] Instalar **uv** (`winget install astral-sh.uv` no Windows) e verificar (`uv --version`)
- [ ] `uv init` → `pyproject.toml` com dependências iniciais (fastapi, uvicorn, pydantic, xgboost, scikit-learn, pandas, shap) e grupo dev (pytest, httpx)
- [ ] `uv sync` sem erros (cria `.venv/` e `uv.lock` automaticamente — commitar o `uv.lock`)

### 3.3. Dataset (spec 3.2 — passo 1)
- [ ] Criar conta Kaggle e aceitar regras da competição *Home Credit Default Risk*
- [ ] Configurar Kaggle CLI (`kaggle.json` — **fora do Git**)
- [ ] Baixar dataset para `data/raw/` (~2.5 GB)
- [ ] Análise exploratória local com pandas (amostra) — validar colunas usadas na spec 3.3
- [ ] Documentar achados da exploração em `notebooks/eda_local.ipynb`

### 3.4. Esqueleto da API (spec 10)
- [ ] `src/api/main.py` com `GET /health`
- [ ] `src/api/schemas.py` com `CreditRequest` (Pydantic v2: `income`, `age`, `avg_spend_90d`, `total_late_payments`, `current_bureau_score`)
- [ ] `POST /predict` com modelo *stub* (retorna score simulado até a Fase 2 entregar o modelo real)
- [ ] Estrutura `src/api/services/` (inference.py e logging_bq.py como stubs)
- [ ] Rodar localmente: `uv run uvicorn src.api.main:app` e validar Swagger em `/docs`

### 3.5. Testes e CI (spec 11 e 14)
- [ ] `tests/test_api.py` (health + predict com payload válido e inválido)
- [ ] `uv run pytest` verde localmente
- [ ] Workflow `.github/workflows/ci.yml` — **apenas testes** nesta fase (setup com `astral-sh/setup-uv` + `uv sync`, sem deploy)
- [ ] CI verde no GitHub após push

### 3.6. Docker local (spec 13)
- [ ] `Dockerfile` conforme spec (sem modelo embutido; dependências instaladas via `uv sync --frozen` a partir de `pyproject.toml` + `uv.lock`)
- [ ] `docker build` e `docker run` locais funcionando (`/health` responde na porta 8080)

**✅ Critério de saída da Fase 0:** CI verde no repositório público + API rodando em Docker local + dataset explorado.

---

## 4. FASE 1 — GCP e Dados na Nuvem ⚪ NÃO INICIADA

> **Objetivo:** infraestrutura GCP provisionada com proteção de custos e dados na camada Bronze.

### 4.1. Conta e projeto GCP (spec 1.1)
- [ ] Criar conta GCP (ativar $300 de crédito)
- [ ] Criar projeto GCP: nome de exibição **"Banco_DataBricks_ML"**, Project ID **`banco-databricks-ml`** — anotar o ID (*IDs GCP não aceitam maiúsculas nem underscores*)
- [ ] **Budget Alert de $250 (50/75/90%) — ANTES de qualquer recurso** (spec 1.6)
- [ ] Habilitar APIs: Cloud Run, Cloud Storage, BigQuery, Cloud Build, Artifact Registry, Pub/Sub, Cloud Logging
- [ ] Criar Service Account `credit-ai-sa` com roles granulares (Cloud Run Admin, Storage Object Admin, BigQuery Data Editor, BigQuery Job User, Cloud Build Editor)
- [ ] Gerar chave JSON → `gcp-key.json` (**confirmar que está no .gitignore**)
- [ ] Instalar e configurar gcloud CLI (`gcloud init`, `auth login`, `config set project banco-databricks-ml`)

### 4.2. Storage e dados (spec 1.1 e 3.2)
- [ ] Criar buckets `gs://fintech-models-bucket` e `gs://fintech-data-raw`
- [ ] Upload dos CSVs: `gsutil -m cp data/raw/*.csv gs://fintech-data-raw/home-credit/`
- [ ] Configurar DVC (`dvc init` + remote `gs://fintech-data-raw/dvc-store`)
- [ ] Rastrear dados com `dvc import-url ... --no-download` (sem duplicar os 2.5 GB)

### 4.3. Terraform (spec 12)
- [ ] `infra/terraform/` com providers e backend configurados
- [ ] Recursos: bucket de modelos, Artifact Registry `credit-api`, BigQuery dataset `credit_risk_features`
- [ ] `terraform plan` e `apply` sem erros (Cloud Run fica para a Fase 3)

### 4.4. Secrets do CI/CD (spec 1.5)
- [ ] Adicionar `GCP_SA_KEY` e `GCP_PROJECT_ID` nos Secrets do GitHub Actions

**✅ Critério de saída da Fase 1:** dados no GCS + Terraform aplicado + budget alert ativo + secrets configurados.

---

## 5. FASE 2 — Databricks e Modelo ⚪ NÃO INICIADA

> ⏰ **ATENÇÃO:** o Trial dura **14 dias**. Só ativar quando os notebooks estiverem escritos e a lógica validada localmente (itens 5.1). O relógio começa no item 5.2.

### 5.1. Pré-trial (preparação local, sem custo)
- [ ] Escrever notebook de feature engineering (spec 7) — validar lógica com PySpark local ou pandas em amostra
- [ ] Escrever script de treinamento (spec 8) — validar XGBoost em amostra local
- [ ] Escrever notebook de drift/Evidently (spec 16) — validar com dados simulados
- [ ] Definir `ml_pipeline.py` (criação dos jobs via Databricks SDK/CLI)

### 5.2. Ativação e setup do workspace (spec 1.2) — ⏰ INICIA OS 14 DIAS
- [ ] Criar conta Trial **Databricks on Google Cloud**
- [ ] Configurar workspace + pasta `credit-risk-project`
- [ ] Criar cluster `credit-risk-cluster` (Runtime 13.3 LTS, e2-standard-4, auto-termination 30 min)
- [ ] Conectar ao GCP (credenciais da SA no cluster)
- [ ] Conectar Repos ao GitHub `Banco_DataBricks_ML`

### 5.3. Pipeline de dados (spec 3.2 e 7)
- [ ] Ingestão Bronze: CSVs do GCS → tabelas Delta (`bronze_*`)
- [ ] Executar feature engineering → tabela `gold_credit_features`
- [ ] Validar schema da Gold = contrato da API (paridade treino/serving)
- [ ] Exportar Gold para BigQuery (`credit_risk_features`)

### 5.4. Treinamento e MLOps (spec 8 e 9)
- [ ] Treinar XGBoost com tracking MLflow (`/Shared/Credit_Risk_Analysis`)
- [ ] Avaliar métricas: **AUC-ROC > 0.85 e KS > 40** (critério de aceite do modelo)
- [ ] Registrar modelo `credit-risk-classifier` no MLflow Model Registry
- [ ] Promover a `Production` e exportar `model.bst` para `gs://fintech-models-bucket/v1/`
- [ ] Criar job `credit-risk-training` (mensal) e `drift-monitoring` (semanal) nos Workflows

**✅ Critério de saída da Fase 2:** modelo em Production no Registry + artefato no GCS + jobs agendados + métricas atingidas.

---

## 6. FASE 3 — Deploy, CI/CD Completo e Monitoramento ⚪ NÃO INICIADA

### 6.1. API com modelo real (spec 10)
- [ ] Substituir stub: carregar `model.bst` do GCS no startup (lifespan)
- [ ] Implementar explicabilidade SHAP (top 3 features na resposta)
- [ ] Implementar log assíncrono de predições no BigQuery (`prediction_logs`)
- [ ] Testes de integração atualizados e verdes

### 6.2. Deploy no Cloud Run (spec 11, 12 e 13)
- [ ] Adicionar recurso Cloud Run `credit-risk-api` no Terraform (com `lifecycle.ignore_changes` na imagem) e aplicar
- [ ] Completar workflow CI/CD: testes → build (Artifact Registry, tag por SHA) → deploy Cloud Run
- [ ] Deploy funcionando via push na `main`
- [ ] Validar Swagger UI público e latência < 200ms (p95)

### 6.3. Monitoramento (spec 16)
- [ ] Job Evidently comparando `prediction_logs` × dataset de referência
- [ ] Relatórios HTML em `gs://fintech-models-bucket/reports/`
- [ ] Alerta Pub/Sub → Cloud Logging quando drift > threshold
- [ ] Dashboards Cloud Monitoring (latência, 5xx, memória)

### 6.4. Testes de carga e encerramento
- [ ] Teste de carga com Locust (validar SLA)
- [ ] Revisão final de segurança: nenhum secret no repo público, IAM mínimo
- [ ] README final com instruções de reprodução, prints do Swagger e resultados do modelo
- [ ] `terraform destroy` dos recursos caros após demonstrações (higiene de custos)

**✅ Critério de saída da Fase 3:** API pública no Cloud Run com modelo real + CI/CD completo + drift monitorado = **projeto demonstrável em entrevista**.

---

## 7. Riscos e Mitigações

| # | Risco | Impacto | Mitigação |
| :--- | :--- | :--- | :--- |
| 1 | Trial Databricks expira antes do fim da Fase 2 | Alto | Preparar tudo na etapa 5.1 antes de ativar; concentrar execução nos 14 dias |
| 2 | Estouro dos $300 de crédito GCP | Alto | Budget alert em $250; auto-termination; `terraform destroy` pós-demo |
| 3 | Vazamento de credenciais (repo público) | Crítico | `.gitignore` primeiro; secrets só no GitHub Actions; revisão antes de cada push |
| 4 | Modelo não atinge AUC > 0.85 | Médio | Baseline conhecido da competição (~0.75–0.78 com poucas features); ajustar meta ou enriquecer features com `bureau.csv` |
| 5 | Community/Trial sem algum recurso esperado | Médio | Validado na spec: Trial Premium on GCP cobre Repos, Jobs e GCS |

---

## 8. Definition of Done (por atividade)

Uma atividade só é marcada `[x]` quando:
1. Código revisado e commitado na `main` (ou branch mergeada via PR)
2. Testes relacionados verdes no CI
3. Sem credenciais expostas
4. Documentação/README atualizado quando aplicável

---

## 9. Histórico de Progresso

| Data | Fase | Atividade | Observação |
| :--- | :--- | :--- | :--- |
| 29/07/2026 | — | PRD criado | Início do projeto |
| 29/07/2026 | — | PRD atualizado | Adoção do **uv** (pyproject.toml/uv.lock) no lugar de requirements.txt; projeto GCP renomeado para **Banco_DataBricks_ML** (ID `banco-databricks-ml`) |
