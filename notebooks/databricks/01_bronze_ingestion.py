# Databricks notebook source
# MAGIC %md
# MAGIC # 01 — Ingestão Bronze: GCS → Delta Lake
# MAGIC
# MAGIC Lê os CSVs do Home Credit em `gs://fintech-data-raw/home-credit/` e grava
# MAGIC as tabelas Delta da camada **Bronze** (spec seções 3.2 e 4).
# MAGIC
# MAGIC **Pré-requisito:** cluster com a Service Account `credit-ai-sa` configurada
# MAGIC (GOOGLE_APPLICATION_CREDENTIALS) para leitura do GCS.

# COMMAND ----------

RAW_PATH = "gs://fintech-data-raw/home-credit"

# Tabelas usadas no pipeline (spec 3.1). As demais podem ser ingeridas depois
# para enriquecimento de features (bureau, previous_application etc.).
TABLES = [
    "application_train",
    "application_test",
    "installments_payments",
    "credit_card_balance",
    "bureau",
]

# COMMAND ----------

for table in TABLES:
    df = (
        spark.read.format("csv")
        .option("header", "true")
        .option("inferSchema", "true")
        .load(f"{RAW_PATH}/{table}.csv")
    )
    df.write.format("delta").mode("overwrite").saveAsTable(f"bronze_{table}")
    print(f"bronze_{table}: {df.count():,} registros")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Validação rápida

# COMMAND ----------

display(spark.sql("SHOW TABLES LIKE 'bronze_*'"))
display(spark.table("bronze_application_train").limit(5))
