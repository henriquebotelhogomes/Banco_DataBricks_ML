# Databricks notebook source
# MAGIC %md
# MAGIC # 04 — Monitoramento de Drift (Evidently AI)
# MAGIC
# MAGIC Job semanal **drift-monitoring** (spec seção 16):
# MAGIC 1. Referência: amostra da `gold_credit_features` (dados de treino)
# MAGIC 2. Atual: predições logadas pela API no BigQuery (`prediction_logs`)
# MAGIC 3. Relatório HTML → GCS; drift acima do threshold → alerta Pub/Sub
# MAGIC
# MAGIC Requer no cluster: `evidently>=0.4`, `google-cloud-pubsub`.

# COMMAND ----------

import json

from evidently import ColumnMapping
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

FEATURES = ["income", "age", "avg_spend_90d", "total_late_payments", "current_bureau_score"]
REPORT_GCS = "gs://fintech-models-bucket/reports"
DRIFT_SHARE_THRESHOLD = 0.5  # alerta se >50% das features driftaram

# COMMAND ----------

# Referência: dados de treinamento (Gold)
reference = (
    spark.table("gold_credit_features").select(*FEATURES).sample(0.1, seed=42).toPandas()
)

# Atual: requisições reais recebidas pela API (janela de 7 dias)
current = (
    spark.read.format("bigquery")
    .option("table", "banco-databricks-ml.credit_risk_features.prediction_logs")
    .load()
    .filter("timestamp >= current_date() - interval 7 days")
    .select(*FEATURES)
    .toPandas()
)
print(f"referência: {len(reference):,} | atual: {len(current):,}")

# COMMAND ----------

report = Report(metrics=[DataDriftPreset()])
report.run(
    reference_data=reference,
    current_data=current,
    column_mapping=ColumnMapping(numerical_features=FEATURES),
)

result = report.as_dict()["metrics"][0]["result"]
drift_share = result["share_of_drifted_columns"]
dataset_drift = result["dataset_drift"]
print(f"share_of_drifted_columns={drift_share:.2f} | dataset_drift={dataset_drift}")

# COMMAND ----------

# Relatório HTML no GCS (evidência para auditoria)
from datetime import date

local_path = f"/tmp/drift_report_{date.today()}.html"
report.save_html(local_path)
dbutils.fs.cp(f"file:{local_path}", f"{REPORT_GCS}/drift_report_{date.today()}.html")
print(f"Relatório salvo em {REPORT_GCS}/drift_report_{date.today()}.html")

# COMMAND ----------

# Alerta via Pub/Sub → Cloud Logging (spec seção 16)
if dataset_drift or drift_share > DRIFT_SHARE_THRESHOLD:
    from google.cloud import pubsub_v1

    publisher = pubsub_v1.PublisherClient()
    topic = publisher.topic_path("banco-databricks-ml", "drift-alerts")
    payload = json.dumps(
        {
            "severity": "WARNING",
            "model": "credit-risk-classifier",
            "drift_share": drift_share,
            "dataset_drift": dataset_drift,
            "report": f"{REPORT_GCS}/drift_report_{date.today()}.html",
        }
    ).encode()
    publisher.publish(topic, payload).result()
    print("⚠️ ALERTA de drift publicado no Pub/Sub (topic: drift-alerts)")
else:
    print("Sem drift relevante — nenhum alerta emitido.")
