# PRD — Sistema de Avaliação de Risco de Crédito com IA

**Product Requirements Document / Plano de Implementação com Checklists**

| Campo | Valor |
| :--- | :--- |
| **Projeto** | Sistema de Avaliação de Risco de Crédito com IA (FinTech Solutions S.A.) |
| **Repositório** | [github.com/henriquebotelhogomes/Banco_DataBricks_ML](https://github.com/henriquebotelhogomes/Banco_DataBricks_ML) — **público** |
| **Documento base** | [FinTech Solutions S.A.md](./FinTech%20Solutions%20S.A.md) (especificação técnica) |
| **Objetivo** | Projeto demo para demonstrar as competências da vaga em [descricao_vaga.md](./descricao_vaga.md) |
| **Status geral** | 🟡 Fase 1 em andamento — projeto GCP e budget criados |
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

## 3. FASE 0 — Fundação Local (custo zero) ✅ CONCLUÍDA

> **Objetivo:** repositório funcional com API esqueleto, testes e CI verde — sem gastar créditos nem ativar trials.

### 3.1. Repositório e Git
- [x] Criar `.gitignore` (`.venv/`, `.env`, `gcp-key.json`, `data/`, `__pycache__`, `*.bst`, `.dvc/cache`)
- [x] Inicializar Git local e conectar ao remote `https://github.com/henriquebotelhogomes/Banco_DataBricks_ML`
- [x] Criar `README.md` com visão geral, arquitetura e badge de CI
- [x] Commit inicial com PRD + especificação + descrição da vaga
- [x] Criar estrutura de pastas (seção 2 deste PRD)

### 3.2. Ambiente local (spec 1.4) — gerenciado com **uv**
- [x] Python 3.11+ instalado e verificado (3.11.15 fixado via `.python-version` / host com 3.12)
- [x] Docker Desktop instalado e verificado (29.6.1)
- [x] Instalar **uv** (0.11.25 já presente) e verificar (`uv --version`)
- [x] `pyproject.toml` com dependências iniciais (fastapi, uvicorn, pydantic, xgboost, scikit-learn, pandas, shap) e grupo dev (pytest, httpx)
- [x] `uv sync` sem erros (criou `.venv/` e `uv.lock` — lockfile commitado)

### 3.3. Dataset (spec 3.2 — passo 1)
- [x] Criar conta Kaggle e aceitar regras da competição *Home Credit Default Risk*
- [x] Configurar Kaggle CLI (`kaggle.json` em `~/.kaggle` — **fora do Git**)
- [x] Baixar dataset para `data/raw/` (688 MB zip → ~2.5 GB, 10 arquivos extraídos)
- [x] Análise exploratória local com pandas (amostra) — colunas da spec 3.3 validadas
- [x] Documentar achados da exploração em `src/data/eda_local.py` (script reproduzível via `uv run`)

### 3.4. Esqueleto da API (spec 10)
- [x] `src/api/main.py` com `GET /health`
- [x] `src/api/schemas.py` com `CreditRequest` (Pydantic v2: `income`, `age`, `avg_spend_90d`, `total_late_payments`, `current_bureau_score`) + `CreditResponse`
- [x] `POST /predict` com modelo *stub* (retorna score simulado até a Fase 2 entregar o modelo real)
- [x] Estrutura `src/api/services/` (inference.py e logging_bq.py como stubs)
- [x] Rodar localmente e validar (validado via testes + container Docker)

### 3.5. Testes e CI (spec 11 e 14)
- [x] `tests/test_api.py` (health + predict válido/inválido — 7 testes, incl. validações Pydantic)
- [x] `uv run pytest` verde localmente (7/7 passed)
- [x] Workflow `.github/workflows/ci.yml` — **apenas testes** nesta fase (setup com `astral-sh/setup-uv` + `uv sync --frozen`, sem deploy)
- [x] CI verde no GitHub após push ([run #1 — success](https://github.com/henriquebotelhogomes/Banco_DataBricks_ML/actions/runs/30468592212))

### 3.6. Docker local (spec 13)
- [x] `Dockerfile` conforme spec (sem modelo embutido; dependências via `uv sync --frozen --no-dev`)
- [x] `docker build` e `docker run` locais funcionando (`/health` e `/predict` validados na porta 8080)

**✅ Critério de saída da Fase 0:** CI verde no repositório público + API rodando em Docker local + dataset explorado.

---

## 4. FASE 1 — GCP e Dados na Nuvem 🟡 EM ANDAMENTO

> **Objetivo:** infraestrutura GCP provisionada com proteção de custos e dados na camada Bronze.
>
> ⚠️ **SEM crédito gratuito de $300** — a conta GCP existente não tem direito ao trial; **todo consumo é cobrado em dinheiro real (BRL)**. Orçamento definido: **R$ 170/mês (≈ US$ 30)**. Disciplina de custos é obrigatória: desligar tudo após o uso e `terraform destroy` pós-demo.

### 4.1. Conta e projeto GCP (spec 1.1)
- [x] Conta GCP existente (`henriquebotelho1@gmail.com`) — **sem os $300 de crédito**
- [x] Criar projeto GCP: nome de exibição **"Banco DataBricks ML"** (sem underscores — restrição do GCP), Project ID **`banco-databricks-ml`**, Project Number `1003760453129` — ATIVO
- [x] Vincular billing (conta `013D5E-D6580A-B1D79D` — E-commerce Analytics Billing)
- [x] **Budget Alert: R$ 170/mês com alertas em 50%/75%/90%, filtrado apenas para este projeto** (budget `66a68d98`)
- [x] Habilitar APIs: Cloud Run, Cloud Storage, BigQuery, Cloud Build, Artifact Registry, Pub/Sub, Cloud Logging
- [x] Criar Service Account `credit-ai-sa` com roles granulares (Cloud Run Admin, Storage Object Admin, BigQuery Data Editor, BigQuery Job User, Cloud Build Editor)
- [x] Gerar chave JSON → `gcp-key.json` (confirmado ignorado pelo Git via `git check-ignore`)
- [x] Instalar e configurar gcloud CLI (SDK 578.0.0 via winget; `auth login` OK; projeto padrão setado)

### 4.2. Storage e dados (spec 1.1 e 3.2)
- [x] Criar buckets `gs://fintech-models-bucket` e `gs://fintech-data-raw` (us-central1, UBLA)
- [x] Upload dos CSVs para `gs://fintech-data-raw/home-credit/` (10 arquivos, 2.68 GB, ~20 MiB/s)
- [x] Configurar DVC com extra `[gs]` (`dvc init` + remote `gs://fintech-data-raw/dvc-store`)
- [x] Rastrear dados com `dvc import-url --no-download` → `data/home-credit.dvc` versionado no Git (sem duplicar os 2.68 GB)

### 4.3. Terraform (spec 12)
- [x] `infra/terraform/main.tf` com provider google ~> 6.0 (Terraform 1.15.8 instalado via winget)
- [x] Recursos: buckets (importados ao estado via `terraform import`), Artifact Registry `credit-api`, BigQuery dataset `credit_risk_features`
- [x] `terraform apply` — 2 added, 0 changed, 0 destroyed (Cloud Run fica para a Fase 3)

### 4.4. Secrets do CI/CD (spec 1.5)
- [ ] Adicionar `GCP_SA_KEY` e `GCP_PROJECT_ID` nos Secrets do GitHub Actions — 🙋 **ação manual do usuário** (UI do GitHub; só é bloqueante na Fase 3)

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
| 2 | Estouro de custos GCP (**sem crédito gratuito — gasto real em BRL**) | Crítico | Budget alert de R$ 170 filtrado ao projeto; auto-termination; `terraform destroy` pós-demo; Cloud Run scale-to-zero |
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
| 29/07/2026 | Fase 0 | Fundação implementada | Estrutura, API stub (FastAPI + Pydantic v2), 7 testes verdes, CI, Docker validado, push na `main` (commit `0ca8b2d`). Pendentes: dataset Kaggle (3.3) e confirmação do CI verde |
| 29/07/2026 | Fase 0 | ✅ **Fase 0 concluída** | Dataset Home Credit baixado (~2.5 GB) e EDA validou o mapeamento da spec 3.3. Achados: default 8.07% (desbalanceado), EXT_SOURCE_1 com 56% de nulos, atraso >30d é raro por parcela (0.32%), outliers de income (max 117M) |
| 29/07/2026 | Fase 1 | Projeto GCP + Budget | gcloud SDK 578 instalado; projeto `banco-databricks-ml` criado (number 1003760453129); billing vinculado; **Budget R$ 170/mês (50/75/90%) filtrado ao projeto**. ⚠️ Conta sem os $300 de crédito — custos reais |
| 29/07/2026 | Fase 1 | Infra provisionada | 7 APIs habilitadas; SA `credit-ai-sa` (5 roles granulares) + chave local; buckets criados e CSVs no GCS (2.68 GB); DVC com `import-url --no-download`; Terraform 1.15.8 aplicado (Artifact Registry + BigQuery dataset; buckets importados). Pendente: secrets no GitHub (manual) |
