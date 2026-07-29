# FinTech Solutions S.A.

## Sistema de Avaliação de Risco de Crédito com IA

**Especificação Técnica de Engenharia de IA e MLOps para o Segmento Financeiro**

*29 de julho de 2026*

---

## 1. Pré-requisitos e Setup Completo — Passo a Passo

Esta seção descreve os procedimentos iniciais necessários para configurar o ambiente de nuvem, processamento de dados e desenvolvimento local.

### 1.1. A. Configuração do Google Cloud Platform (GCP)

1.  **Criar conta GCP:**
    -   Acesse **https://cloud.google.com/**.
    -   Clique em **"Get started for free"**.
    -   Forneça os dados da sua **Google Account**.
    -   Configure o **billing** (cartão de crédito é necessário, mas há `$300` de crédito gratuito para novos usuários).
    -   Crie um novo projeto: nome de exibição **"Banco_DataBricks_ML"**, Project ID **`banco-databricks-ml`** (IDs GCP não aceitam maiúsculas nem underscores).
    -   **Anotar o Project ID** para uso posterior.

2.  **Habilitar APIs necessárias:**
    -   As seguintes APIs devem estar ativas: **Cloud Run API**, **Cloud Storage API**, **BigQuery API**, **Cloud Build API**, **Artifact Registry API**, **Pub/Sub API** e **Cloud Logging API**.
    -   *Como habilitar:* No Console GCP, vá em **APIs & Services** > **Library** > busque por cada API nominalmente > clique em **Enable**.

3.  **Criar Service Account:**
    -   Vá em **Console GCP** > **IAM & Admin** > **Service Accounts** > **Create Service Account**.
    -   Nome: **"credit-ai-sa"**.
    -   **Roles (Papéis):** Adicione *Cloud Run Admin*, *Storage Object Admin*, *BigQuery Data Editor*, *BigQuery Job User* e *Cloud Build Editor* — roles granulares, alinhadas ao princípio do menor privilégio (seção 17).
    -   **Criar chave JSON:** Após criar a conta, vá na aba **Keys** > **Add Key** > **Create new key** > **JSON**.
    -   Baixe o arquivo, renomeie para **"gcp-key.json"** e adicione-o ao seu `.gitignore` (NUNCA envie este arquivo para o GitHub).

4.  **Instalar Google Cloud CLI (gcloud):**
    -   Download em **https://cloud.google.com/sdk/docs/install**.
    -   Siga as instruções para seu sistema operacional (**Linux/Mac/Windows**).
    -   No terminal, execute:
        -   `gcloud init`
        -   `gcloud auth login`
        -   `gcloud config set project banco-databricks-ml`

5.  **Criar buckets no Cloud Storage:**
    -   Crie os seguintes buckets via console ou CLI:
        -   `gs://fintech-models-bucket` (para artefatos de modelo).
        -   `gs://fintech-data-raw` (para dados brutos).
    -   *Nota:* a Feature Store do projeto é o **BigQuery** (seções 4 e 12) — não é necessário bucket dedicado a features.

### 1.2. B. Configuração do Databricks — Passo a Passo Completo

1.  **Criar conta Databricks:**
    -   Acesse **https://www.databricks.com/try-databricks**.
    -   Escolha o plano **"Trial"** (Premium com 14 dias) — *obrigatório para este projeto*, pois o Community Edition não possui Repos, Jobs, nem conectividade externa com GCS/BigQuery, recursos necessários ao pipeline completo.
    -   Crie a conta preferencialmente com um e-mail corporativo.
    -   Para integração nativa, escolha **Databricks on Google Cloud** (o workspace será provisionado dentro do seu projeto GCP e consumirá parte dos $300 de crédito).

2.  **Configurar Workspace:**
    -   Após o login, explore a interface lateral: **Workspace** (arquivos), **Repos** (Git), **Data** (tabelas), **Compute** (clusters) e **Models** (MLflow).
    -   Crie um diretório de projeto: **Workspace** > **Create** > **Folder** > **"credit-risk-project"**.

3.  **Criar e configurar Cluster:**
    -   Vá em **Compute** > **Create Cluster**.
    -   Nome: **"credit-risk-cluster"**.
    -   **Runtime:** Escolha **"Runtime 13.3 LTS (includes Apache Spark 3.4.1, Scala 2.12)"**.
    -   **Access Mode:** Selecione **"Data"** ou **"Single User"** para uso de PySpark.
    -   **Worker type:** o menor disponível (**e2-standard-4**) é suficiente para testes.
    -   *Nota:* Em produção, utilizaremos clusters com auto-scaling.
    -   **Advanced options** > **Spark Config:** Adicione as credenciais do GCP se necessário.
    -   Clique em **"Create Cluster"** e aguarde o status ficar verde.

4.  **Conectar Databricks ao GCP:**
    -   **Opção 1 (Recomendada):** Em **Advanced Options** > **Init Scripts**, adicione um script que configure a chave do GCP.
    -   **Opção 2:** Instale a biblioteca `google-cloud-storage` via **Libraries** > **Install New** > **PyPI**.
    -   Configure as variáveis de ambiente no cluster: **GOOGLE_APPLICATION_CREDENTIALS** e **GCP_PROJECT_ID**.

5.  **Importar dados para o Databricks:**
    -   A ingestão oficial segue o fluxo da seção 3.2: **Kaggle → `gs://fintech-data-raw/home-credit/` → tabelas Delta Bronze** (sem upload manual de CSV).
    -   **Conexão BigQuery:** Use o **Spark BigQuery connector** em clusters configurados com a Service Account do GCP.
    -   *Exploração:* Clique nas tabelas Bronze criadas para visualizar o **schema** e uma amostra dos dados.

6.  **Criar e executar Notebooks:**
    -   **Workspace** > **Create** > **Notebook** > nome **"feature_engineering"**.
    -   Linguagem: **Python**.
    -   Anexe o notebook ao cluster criado no dropdown superior.
    -   *Dica:* Use `Shift+Enter` para executar uma célula. Utilize `display(df)` para visualizar DataFrames e `spark.table("nome")` para ler dados.

7.  **Databricks Repos (Git Integration):**
    -   Vá em **Repos** > **Add Repo**.
    -   Insira a URL do seu repositório GitHub. Isso permite versionar seus notebooks diretamente.

8.  **MLflow no Databricks:**
    -   O MLflow já vem integrado ao workspace — a configuração de tracking, o Model Registry e a governança de estágios estão centralizados nas seções 1.3 e 9 (evitando configuração duplicada).

### 1.3. C. Configuração do MLflow Model Registry e Databricks Workflows

1.  **MLflow Model Registry (Databricks):**
    -   O MLflow já vem integrado ao workspace. Acesse **Models** na barra lateral para gerenciar as versões do modelo `credit-risk-classifier`.
    -   Estágios de promoção: **None** → **Staging** → **Production**. A promoção para *Production* dispara a exportação do artefato para `gs://fintech-models-bucket`.

2.  **Databricks Workflows (Jobs):**
    -   Vá em **Workflows** > **Create Job**.
    -   Job **"credit-risk-training"**: aponta para o notebook de treinamento, agendamento mensal, executando em *job cluster* (mais barato que cluster interativo).
    -   Job **"drift-monitoring"**: agendamento semanal, executa o notebook do **Evidently AI** (ver seção 16).

3.  **Exportação do modelo para o Cloud Storage:**
    -   O passo final do job de treinamento copia o artefato `model.bst` para `gs://fintech-models-bucket/v1/`, de onde a API (Cloud Run) o carrega no startup.

### 1.4. D. Configuração do Ambiente de Desenvolvimento Local

1.  **Instalar Python 3.11+:**
    -   Baixe em **python.org** ou use o **pyenv**. Verifique com `python --version`.

2.  **Instalar Docker:**
    -   Instale o **Docker Desktop**. Verifique a instalação com `docker --version`.

3.  **Instalar uv (gerenciador de pacotes e ambientes):**
    ```bash
    # Windows
    winget install astral-sh.uv
    # Linux/Mac
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

4.  **Clonar repositório e setup:**
    ```bash
    git clone https://github.com/henriquebotelhogomes/Banco_DataBricks_ML.git
    cd Banco_DataBricks_ML
    uv sync   # cria .venv e instala dependências de pyproject.toml + uv.lock
    ```

5.  **Configurar DVC (Data Version Control):**
    ```bash
    uv add dvc
    uv run dvc init
    uv run dvc remote add -d storage gs://fintech-data-raw/dvc-store
    ```

6.  **Configurar variáveis de ambiente (.env):**
    -   Crie um arquivo **.env** na raiz:
        -   **GCP_PROJECT_ID**=banco-databricks-ml
        -   **GCP_SA_KEY_PATH**=./gcp-key.json
        -   **DATABRICKS_HOST**=https://xxx.gcp.databricks.com
        -   **DATABRICKS_TOKEN**=dapi-seu-token-aqui

7.  **Instalar Databricks CLI (nova CLI unificada):**
    ```bash
    # Windows
    winget install Databricks.DatabricksCLI
    # Linux/Mac
    curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh
    # Autenticação (host + token)
    databricks configure
    ```
    -   *Nota:* a antiga `pip install databricks-cli` é legada e não recebe mais atualizações.

### 1.5. E. Configuração do GitHub Actions (CI/CD)

1.  **Adicionar Secrets no GitHub:**
    -   No seu repositório: **Settings** > **Secrets and Variables** > **Actions**.
    -   Adicione: **GCP_SA_KEY** (cole o conteúdo do arquivo JSON) e **GCP_PROJECT_ID**.

### 1.6. F. Gestão de Custos do Crédito GCP ($300)

Como toda a infraestrutura será provisionada de verdade, é essencial controlar o consumo do crédito gratuito:

1.  **Criar Budget Alert:** **Billing** > **Budgets & alerts** > **Create Budget** > valor **$250** com alertas em **50%, 75% e 90%**.
2.  **Estimativa de consumo mensal do projeto:**
    -   Databricks on GCP (Trial 14 dias, cluster pequeno): ~$30–50 em GCE/GKE subjacente.
    -   Databricks Jobs (treinamento mensal + drift semanal, em *job clusters*): ~$5–15/mês.
    -   Cloud Run (scale-to-zero), BigQuery (< 10 GB) e Cloud Storage: custo marginal (~$1–5).
3.  **Regras de higiene:** desligar clusters Databricks após o uso (configurar *auto-termination* de 30 min); preferir *job clusters* a clusters interativos nos Workflows; usar `terraform destroy` ao final de cada ciclo de testes.

---

## 2. Título e Visão Geral

### 2.1. Contexto do Negócio
No cenário financeiro atual, a agilidade na concessão de crédito aliada à precisão na análise de risco é um diferencial competitivo crítico. Este projeto visa substituir modelos estatísticos tradicionais (Score de Crédito) por uma solução de Machine Learning de ponta, capaz de processar grandes volumes de dados estruturados e não estruturados para prever a probabilidade de inadimplência (*default*) de novos proponentes.

### 2.2. Objetivos
*   Reduzir a taxa de inadimplência em **15%** no primeiro ano de operação.
*   Automatizar **80%** das decisões de crédito de baixo risco.
*   Garantir a explicabilidade do modelo (**SHAP/LIME**) para conformidade regulatória.
*   Implementar um ciclo de vida de ML (**MLOps**) totalmente automatizado.

### 2.3. Métricas de Sucesso
*   **Métricas de ML:** AUC-ROC > **0.72**, KS (Kolmogorov-Smirnov) > **32**.
    -   *Racional (ajustado em 29/07/2026):* metas calibradas por validação empírica local com as **5 features do contrato da API** sobre os 307k clientes do Home Credit (AUC 0.725 / KS 34.3). Referência externa: o vencedor da competição Kaggle atingiu ~0.805 usando centenas de features — a meta original de 0.85 era inatingível neste dataset. O foco do projeto é a **engenharia de IA/MLOps ponta a ponta**; o ganho de AUC via enriquecimento de features (`bureau.csv`, `previous_application.csv`) está documentado como evolução futura no backlog do PRD.
*   **Métricas de Negócio:** Redução do *Time-to-Decision* de **48h** para **< 5 segundos**.
*   **Métricas de Engenharia:** Disponibilidade da API de **99.9% (SLA)** e latência de inferência **< 200ms**.

---

## 3. Fonte de Dados para Treinamento

O projeto utilizará o dataset público **Home Credit Default Risk** (Kaggle), que simula fielmente o cenário real de um bureau de crédito: múltiplas tabelas relacionais, histórico transacional e variável alvo de inadimplência.

### 3.1. Descrição do Dataset

| Arquivo | Registros (aprox.) | Conteúdo | Papel no Projeto |
| :--- | :--- | :--- | :--- |
| `application_train.csv` | 307k | Dados cadastrais do proponente + **TARGET** (1 = default) | Tabela principal de treinamento |
| `application_test.csv` | 48k | Proponentes sem label | Simulação de requisições de produção na API |
| `bureau.csv` | 1.7M | Créditos anteriores em outras instituições | Simula dados de **bureau de crédito** |
| `bureau_balance.csv` | 27M | Saldos mensais dos créditos do bureau | Features de comportamento histórico |
| `previous_application.csv` | 1.6M | Propostas anteriores na instituição | Features de relacionamento com o cliente |
| `POS_CASH_balance.csv` | 10M | Saldos mensais de créditos POS/cash | Features de utilização de crédito |
| `installments_payments.csv` | 13.6M | Histórico de pagamentos de parcelas | Base para features de **atraso** (`days_late`) |
| `credit_card_balance.csv` | 3.8M | Saldos mensais de cartão de crédito | Features de gasto (`avg_spend_90d`) |

O volume total (~2.5 GB, dezenas de milhões de linhas nas tabelas transacionais) **justifica o uso de PySpark/Databricks** para os joins e agregações, demonstrando engenharia de dados distribuída de verdade.

### 3.2. Ingestão — Passo a Passo

1.  **Download:** crie uma conta no Kaggle, aceite as regras da competição *Home Credit Default Risk* e baixe via CLI:
    ```bash
    uv tool install kaggle
    kaggle competitions download -c home-credit-default-risk -p ./data/raw
    unzip ./data/raw/home-credit-default-risk.zip -d ./data/raw
    ```
2.  **Upload para a camada Bronze (Cloud Storage):**
    ```bash
    gsutil -m cp ./data/raw/*.csv gs://fintech-data-raw/home-credit/
    ```
3.  **Versionamento com DVC:** os CSVs brutos são imutáveis e já residem em `gs://fintech-data-raw/home-credit/` (fonte canônica). Rastreie-os sem duplicar os ~2.5 GB: `dvc import-url gs://fintech-data-raw/home-credit/ data/raw --no-download`. O remote `dvc-store` fica reservado a artefatos derivados (amostras, datasets processados).
4.  **Leitura no Databricks:** os notebooks PySpark leem diretamente de `gs://fintech-data-raw/home-credit/` (cluster configurado com a Service Account) e gravam as tabelas Delta Bronze.

### 3.3. Mapeamento para o Domínio do Projeto

-   `SK_ID_CURR` → `client_id`
-   `application_train.AMT_INCOME_TOTAL` → `income`
-   `application_train.DAYS_BIRTH` → `age`
-   `installments_payments` (DAYS_ENTRY_PAYMENT − DAYS_INSTALMENT > 30) → `total_late_payments`
-   `credit_card_balance.AMT_BALANCE` (média dos últimos 3 meses) → `avg_spend_90d`
-   `EXT_SOURCE_1/2/3` (média, 0–1) → `current_bureau_score`
-   `TARGET` → `target` (1 = inadimplente)

---

## 4. Arquitetura da Solução

A arquitetura foi desenhada para ser escalável e resiliente, utilizando o melhor do ecossistema Databricks para engenharia de dados e GCP para orquestração de IA. **Toda a infraestrutura será provisionada de verdade no GCP**, utilizando os $300 de crédito gratuito (ver seção 1.6 para gestão de custos).

**Fluxo de Dados:**
1.  **Ingestão:** Os CSVs do **Home Credit Default Risk** (Kaggle) são carregados em `gs://fintech-data-raw` (camada Bronze) e versionados com DVC, simulando dados de fontes transacionais e bureaus de crédito.
2.  **Processamento:** PySpark no **Databricks** realiza limpeza, joins das 7 tabelas relacionais e *Feature Engineering* (arquitetura Medallion Bronze → Silver → Gold em Delta Lake), exportando a tabela Gold de features para o **BigQuery** (Feature Store).
3.  **Treinamento:** O treinamento é orquestrado por **Databricks Workflows (Jobs)** agendados, registrando experimentos e versões no **MLflow** (Tracking + Model Registry). O modelo promovido a *Production* é exportado para `gs://fintech-models-bucket`.
4.  **Serviço:** O modelo é encapsulado em uma **API FastAPI** rodando no **Cloud Run** (Serverless). A interface com o usuário é **exclusivamente via API REST**: a documentação interativa **Swagger UI** (`/docs`) e **ReDoc** (`/redoc`), geradas automaticamente pelo FastAPI, servem como front de demonstração — não haverá frontend dedicado. Cada predição é logada de forma assíncrona na tabela BigQuery `prediction_logs`, insumo do monitoramento de drift.
5.  **Monitoramento:** Um **Databricks Job semanal** executa o **Evidently AI** (open source) para detectar *Data Drift* e *Concept Drift*, publicando alertas via **Pub/Sub**/Cloud Logging; a infraestrutura da API é monitorada pelo **Cloud Monitoring**.

**Consumidores da API:** sistemas de esteira de crédito (integração máquina-a-máquina via JSON/HTTPS), analistas de risco (via Swagger UI) e testes de carga (Locust). A resposta do endpoint `/predict` retorna probabilidade de default, decisão e explicabilidade (top features SHAP).

---

## 5. Stack Tecnológica

| Tecnologia | Versão | Propósito |
| :--- | :--- | :--- |
| **Python** | 3.11+ | Linguagem base para pipelines e modelos |
| **uv** | 0.4+ | Gerenciamento de dependências e ambientes (pyproject.toml + uv.lock) |
| **Databricks** | Runtime 13.x | Processamento distribuído, Feature Engineering e orquestração (Workflows) |
| **MLflow** | 2.x (Databricks) | Tracking de experimentos e Model Registry |
| **Evidently AI** | 0.4+ | Monitoramento de Data/Concept Drift |
| **XGBoost** | 1.7+ | Algoritmo de Gradient Boosting para classificação |
| **FastAPI** | 0.100+ | Framework para API REST de alta performance |
| **Terraform** | 1.5+ | Infraestrutura como Código (IaC) |
| **DVC** | 3.0+ | Versionamento de datasets e artefatos |
| **GitHub Actions** | N/A | Automação de CI/CD |

---

## 6. Estrutura de Pastas do Projeto

```text
Banco_DataBricks_ML/
├── .github/
│   └── workflows/          # Pipelines de CI/CD (GitHub Actions)
├── data/
│   └── raw/                # CSVs do Home Credit (versionados via DVC, fora do Git)
├── infra/
│   └── terraform/          # Definições de recursos GCP
├── notebooks/
│   └── databricks/         # Notebooks PySpark para ETL
├── src/
│   ├── data/               # Scripts de ingestão e processamento
│   ├── models/             # Lógica de treinamento e validação
│   ├── api/                # Código fonte da API FastAPI
│   │   ├── main.py
│   │   ├── schemas.py      # Validação Pydantic
│   │   └── services/       # Lógica de negócio e inferência
│   └── utils/              # Funções auxiliares e logging
├── tests/                  # Testes unitários e de integração
├── Dockerfile              # Build da imagem da API
├── dvc.yaml                # Pipeline de dados DVC
├── ml_pipeline.py          # Orquestração dos Databricks Jobs (treino/drift)
├── pyproject.toml          # Dependências e metadados (gerenciados com uv)
└── uv.lock                 # Lockfile determinístico (uv)
```

---

## 7. Engenharia de Dados (Databricks)

Utilizamos o Databricks para processar as tabelas transacionais do Home Credit (dezenas de milhões de registros — seção 3.1). O foco é a criação de uma *Feature Store* robusta: as tabelas Bronze são unidas por `SK_ID_CURR` (`client_id`) e agregadas na camada Gold, cujo schema é **idêntico ao contrato da API** (seção 10), garantindo paridade treino/serving.

```python
# Notebook: Feature Engineering - Credit Risk (Home Credit)
from pyspark.sql import functions as F

applications = spark.table("bronze_application_train")
installments = spark.table("bronze_installments_payments")
credit_card = spark.table("bronze_credit_card_balance")

def generate_credit_features():
    """
    Gera features agregadas de comportamento financeiro por cliente (SK_ID_CURR).
    """
    # Atraso: pagamento efetuado após a data da parcela (> 30 dias)
    df_late = installments.withColumn(
        "days_late", F.col("DAYS_ENTRY_PAYMENT") - F.col("DAYS_INSTALMENT")
    ).withColumn(
        "has_late_payment", F.when(F.col("days_late") > 30, 1).otherwise(0)
    ).groupBy("SK_ID_CURR").agg(
        F.sum("has_late_payment").alias("total_late_payments")
    )

    # Gasto médio de cartão nos últimos 3 meses (MONTHS_BALANCE >= -3 ≈ 90 dias)
    df_spend = credit_card.filter(F.col("MONTHS_BALANCE") >= -3) \
        .groupBy("SK_ID_CURR").agg(
            F.avg("AMT_BALANCE").alias("avg_spend_90d")
        )

    # Dados cadastrais + score externo médio (proxy de score de bureau, 0–1)
    df_base = applications.select(
        "SK_ID_CURR",
        F.col("TARGET").alias("target"),
        F.col("AMT_INCOME_TOTAL").alias("income"),
        (F.col("DAYS_BIRTH") / -365).cast("int").alias("age"),
        ((F.col("EXT_SOURCE_1") + F.col("EXT_SOURCE_2") + F.col("EXT_SOURCE_3")) / 3
        ).alias("current_bureau_score")
    )

    return df_base \
        .join(df_late, "SK_ID_CURR", "left") \
        .join(df_spend, "SK_ID_CURR", "left") \
        .fillna(0, subset=["total_late_payments", "avg_spend_90d"]) \
        .withColumnRenamed("SK_ID_CURR", "client_id")

# Escrita no Delta Lake (camada Gold)
df_final = generate_credit_features()
df_final.write.format("delta").mode("overwrite").saveAsTable("gold_credit_features")
```

---

## 8. Desenvolvimento do Modelo (Python)

O modelo utiliza XGBoost devido à sua eficiência com dados tabulares e suporte nativo a valores ausentes. O dataset de treino é a tabela Gold de features (seção 7), lida do BigQuery, onde `target` corresponde à coluna **TARGET** do Home Credit (1 = inadimplente). As features (`income`, `age`, `avg_spend_90d`, `total_late_payments`, `current_bureau_score`) são exatamente as mesmas recebidas pela API (seção 10), eliminando risco de *training-serving skew*.

```python
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import mlflow

def train_credit_model(data):
    X = data.drop(columns=['target', 'client_id'])
    y = data['target']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = xgb.XGBClassifier(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=6,
        objective='binary:logistic'
    )
    
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
    
    # Registro no MLflow Model Registry (Databricks)
    mlflow.xgboost.log_model(
        model,
        artifact_path="model",
        registered_model_name="credit-risk-classifier"
    )
    
    # Exportação do artefato para consumo pela API no Cloud Run
    # (passo final do Databricks Job: copia para gs://fintech-models-bucket/v1/)
    model.save_model("model.bst")
    
    return model
```

---

## 9. MLOps

A governança é garantida pelo MLflow para rastreamento de experimentos e Model Registry, e DVC para versionamento de dados. O **registro** do modelo acontece uma única vez, no treinamento (seção 8, via `registered_model_name`); esta seção cuida do **tracking de métricas e da promoção de estágio**.

```python
import mlflow
from mlflow.tracking import MlflowClient

# Configuração do MLflow Tracking (única no projeto — centralizada em src/utils)
mlflow.set_tracking_uri("databricks")
mlflow.set_experiment("/Shared/Credit_Risk_Analysis")

# No run de treinamento (seção 8) são logados parâmetros e métricas:
with mlflow.start_run():
    mlflow.log_param("algorithm", "XGBoost")
    mlflow.log_metric("auc", 0.88)

# Promoção de estágio no Model Registry (após validação das métricas)
client = MlflowClient()
client.transition_model_version_stage(
    name="credit-risk-classifier",
    version=1,
    stage="Production"
)
```

---

## 10. API REST (FastAPI)

A API é o ponto de entrada para as requisições de crédito em tempo real e também a **única interface com o usuário**: a demonstração do sistema é feita via **Swagger UI** (`/docs`), sem frontend dedicado. Em produção (Cloud Run), o modelo (promovido a *Production* no MLflow Registry e exportado para `gs://fintech-models-bucket`) é carregado no startup da aplicação, e a resposta inclui as top features SHAP que justificam a decisão (exigência de explicabilidade regulatória). Cada requisição é logada de forma assíncrona (`BackgroundTasks`) na tabela BigQuery `credit_risk_features.prediction_logs` — insumo do job de drift (seção 16).

```python
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
import pandas as pd

from api.services.inference import model, explainer, get_top_shap_features
from api.services.logging_bq import log_prediction_bq

app = FastAPI(title="Credit Risk Scoring API")

class CreditRequest(BaseModel):
    client_id: str
    income: float = Field(..., gt=0)
    age: int = Field(..., ge=18)
    avg_spend_90d: float = Field(..., ge=0)
    total_late_payments: int = Field(..., ge=0)
    current_bureau_score: float = Field(..., ge=0, le=1)  # média de EXT_SOURCE_1/2/3

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/predict")
async def predict_risk(request: CreditRequest, background_tasks: BackgroundTasks):
    try:
        # Inferência real: modelo carregado do GCS no startup (lifespan)
        input_data = pd.DataFrame([request.model_dump()])  # Pydantic v2
        features = input_data.drop(columns=["client_id"])
        risk_score = float(model.predict_proba(features)[0][1])
        
        # Explicabilidade: top 3 features SHAP da predição
        shap_values = explainer(features)
        top_features = get_top_shap_features(shap_values, n=3)
        
        # Log assíncrono no BigQuery (insumo do monitoramento de drift — seção 16)
        background_tasks.add_task(log_prediction_bq, request.model_dump(), risk_score)
        
        return {
            "client_id": request.client_id,
            "probability_of_default": risk_score,
            "decision": "APPROVED" if risk_score < 0.3 else "REJECTED",
            "explanation": top_features  # ex: [{"feature": "total_late_payments", "impact": 0.12}, ...]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 11. CI/CD Pipeline

Workflow do GitHub Actions para automação do deploy.

```yaml
name: ML Pipeline CI/CD

on:
  push:
    branches: [ main ]

jobs:
  test-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up uv
        uses: astral-sh/setup-uv@v3
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: uv sync --frozen
        
      - name: Run Tests
        run: uv run pytest tests/
        
      - name: Auth GCP
        uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
          
      - name: Build & Push (Artifact Registry)
        run: |
          gcloud builds submit --tag us-central1-docker.pkg.dev/banco-databricks-ml/credit-api/credit-api:${{ github.sha }}

      - name: Deploy to Cloud Run
        # O serviço é provisionado pelo Terraform (seção 12); o CI/CD apenas atualiza a imagem
        run: |
          gcloud run deploy credit-risk-api \
            --image us-central1-docker.pkg.dev/banco-databricks-ml/credit-api/credit-api:${{ github.sha }} \
            --region us-central1 --platform managed
```

---

## 12. Infraestrutura como Código (Terraform)

```hcl
resource "google_storage_bucket" "model_artifacts" {
  name     = "fintech-models-bucket" # mesmo bucket referenciado em todo o projeto
  location = "US"
  uniform_bucket_level_access = true
}

resource "google_artifact_registry_repository" "api_repo" {
  repository_id = "credit-api"
  location      = "us-central1"
  format        = "DOCKER"
}

resource "google_bigquery_dataset" "feature_store" {
  dataset_id = "credit_risk_features"
  location   = "US"
}

resource "google_cloud_run_service" "api_service" {
  name     = "credit-risk-api"
  location = "us-central1"
  template {
    spec {
      containers {
        image = "us-central1-docker.pkg.dev/banco-databricks-ml/credit-api/credit-api:latest"
      }
    }
  }

  # O CI/CD (seção 11) atualiza apenas a imagem; o Terraform ignora esse
  # atributo para não haver drift entre IaC e deploy contínuo.
  lifecycle {
    ignore_changes = [template[0].spec[0].containers[0].image]
  }
}
```

---

## 13. Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

# uv para instalação determinística das dependências (pyproject.toml + uv.lock)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY src/api/ ./api/

# O modelo NÃO é embutido na imagem: é carregado de
# gs://fintech-models-bucket/v1/model.bst no startup da aplicação (lifespan)

EXPOSE 8080

CMD ["uv", "run", "--no-sync", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

---

## 14. Testes

```python
# tests/test_api.py
from fastapi.testclient import TestClient
from src.api.main import app  # pytest executado a partir da raiz do repositório

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_prediction_valid_data():
    payload = {
        "client_id": "12345",
        "income": 5000.0,
        "age": 30,
        "avg_spend_90d": 1250.50,
        "total_late_payments": 0,
        "current_bureau_score": 0.72
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    assert "probability_of_default" in response.json()
```

---

## 15. Metodologia Ágil

*   **Sprints:** Quinzenais (2 semanas).
*   **Cerimônias:** Daily (15 min), Sprint Planning, Review e Retrospective.
*   **User Story Exemplo:** "Como analista de risco, quero que o sistema retorne a probabilidade de inadimplência em menos de 5 segundos para que eu possa aprovar propostas em tempo real." (alinhada à métrica de negócio da seção 2.3)
*   **DoD (Definition of Done):** Código revisado, testes unitários com >80% de cobertura, documentação atualizada e deploy em ambiente de Staging realizado.

---

## 16. Monitoramento e Observabilidade

O monitoramento do modelo é feito com **Evidently AI** (open source), executado no **Databricks Job semanal** `drift-monitoring`, que compara a distribuição das requisições recebidas pela API (logadas por ela própria na tabela BigQuery `credit_risk_features.prediction_logs` — seção 10) com o dataset de referência de treinamento:
*   **Data Drift:** Mudanças na distribuição estatística das features de entrada (ex: queda súbita no score médio dos proponentes).
*   **Concept Drift:** Mudança na relação entre as features e o alvo (ex: mudança no comportamento de pagamento devido a crises macroeconômicas).
*   **Alertas:** Relatórios HTML do Evidently salvos em `gs://fintech-models-bucket/reports/`; quando o drift excede o threshold, o job publica alerta via **Pub/Sub** → Cloud Logging.
*   **Infra:** Latência, taxa de erro 5xx e consumo de memória do Cloud Run via **Cloud Monitoring**.

---

## 17. Segurança e Compliance

*   **LGPD:** Anonimização de dados sensíveis (PII) no Databricks.
*   **Criptografia:** Dados em repouso (AES-256) e em trânsito (TLS 1.2+).
*   **IAM:** Princípio do menor privilégio para Service Accounts.
*   **Explicabilidade:** Uso de SHAP values para justificar negativas de crédito, conforme exigido pelo Banco Central.

---

## 18. Roadmap de Implementação

*   **Sprint 1-2:** Setup da infraestrutura real no GCP (Terraform, Databricks on GCP) e ingestão do dataset Home Credit na camada Bronze (Kaggle → GCS → Delta Lake).
*   **Sprint 3-4:** Feature Engineering e treinamento do modelo baseline (XGBoost).
*   **Sprint 5-6:** Desenvolvimento da API FastAPI e integração com o MLflow Model Registry (promoção → exportação para GCS → Cloud Run).
*   **Sprint 7-8:** Implementação de CI/CD, Testes de Carga e Monitoramento de Drift (Evidently AI).

---
*Documento elaborado em 29 de julho de 2026. As informações contidas são de responsabilidade do solicitante.*