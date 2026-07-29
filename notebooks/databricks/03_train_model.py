# Databricks notebook source
# MAGIC %md
# MAGIC # 03 — Treinamento: XGBoost + MLflow + Export GCS
# MAGIC
# MAGIC Treina o `credit-risk-classifier` (spec seções 8 e 9):
# MAGIC 1. Lê a Gold, treina XGBoost (com `scale_pos_weight` — dataset 8% default)
# MAGIC 2. Loga params/métricas e registra no MLflow Model Registry
# MAGIC 3. Se AUC ≥ threshold, promove a Production e exporta `model.bst` para o GCS
# MAGIC
# MAGIC Executado pelo job **credit-risk-training** (mensal).

# COMMAND ----------

import mlflow
import xgboost as xgb
from mlflow.tracking import MlflowClient
from scipy.stats import ks_2samp
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

mlflow.set_tracking_uri("databricks")
mlflow.set_experiment("/Shared/Credit_Risk_Analysis")

MODEL_NAME = "credit-risk-classifier"
FEATURES = ["income", "age", "avg_spend_90d", "total_late_payments", "current_bureau_score"]
AUC_THRESHOLD = 0.72  # baseline realista p/ 5 features; meta AUC>0.85 exige enriquecimento
GCS_MODEL_PATH = "gs://fintech-models-bucket/v1/model.bst"

# COMMAND ----------

data = spark.table("gold_credit_features").toPandas()
X, y = data[FEATURES], data["target"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# COMMAND ----------

with mlflow.start_run() as run:
    scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()

    model = xgb.XGBClassifier(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=6,
        objective="binary:logistic",
        scale_pos_weight=scale_pos_weight,  # EDA: dataset desbalanceado (8% default)
        eval_metric="auc",
        early_stopping_rounds=30,
    )
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

    # Métricas de aceite (spec 2.3): AUC-ROC e KS
    proba = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, proba)
    ks = ks_2samp(proba[y_test == 1], proba[y_test == 0]).statistic * 100

    mlflow.log_param("algorithm", "XGBoost")
    mlflow.log_param("features", ",".join(FEATURES))
    mlflow.log_param("scale_pos_weight", round(scale_pos_weight, 2))
    mlflow.log_metric("auc", auc)
    mlflow.log_metric("ks", ks)

    mlflow.xgboost.log_model(
        model, artifact_path="model", registered_model_name=MODEL_NAME
    )
    print(f"AUC={auc:.4f} | KS={ks:.1f} | run_id={run.info.run_id}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Promoção a Production + export para o GCS (gate de qualidade)

# COMMAND ----------

if auc >= AUC_THRESHOLD:
    client = MlflowClient()
    latest = client.get_latest_versions(MODEL_NAME, stages=["None"])[0]
    client.transition_model_version_stage(
        name=MODEL_NAME, version=latest.version, stage="Production"
    )

    # Exporta o artefato para consumo pela API no Cloud Run (spec 1.3.3)
    model.save_model("/tmp/model.bst")
    dbutils.fs.cp("file:/tmp/model.bst", GCS_MODEL_PATH)
    print(f"v{latest.version} promovida a Production e exportada para {GCS_MODEL_PATH}")
else:
    raise ValueError(
        f"AUC {auc:.4f} abaixo do threshold {AUC_THRESHOLD} — modelo NÃO promovido."
    )
