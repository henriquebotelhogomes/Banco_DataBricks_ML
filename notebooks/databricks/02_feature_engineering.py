# Databricks notebook source
# MAGIC %md
# MAGIC # 02 — Feature Engineering: Bronze → Gold
# MAGIC
# MAGIC Gera a tabela `gold_credit_features` (spec seção 7), cujo schema é
# MAGIC **idêntico ao contrato da API** (paridade treino/serving):
# MAGIC `client_id, income, age, avg_spend_90d, total_late_payments, current_bureau_score, target`
# MAGIC
# MAGIC Achados da EDA local aplicados aqui:
# MAGIC - `EXT_SOURCE_1` tem 56% de nulos → média ignora nulos (não zera o score)
# MAGIC - outliers de renda (max 117M) → clipping no percentil 99

# COMMAND ----------

from pyspark.sql import functions as F

applications = spark.table("bronze_application_train")
installments = spark.table("bronze_installments_payments")
credit_card = spark.table("bronze_credit_card_balance")

# COMMAND ----------


def generate_credit_features():
    """Gera features agregadas de comportamento financeiro por cliente (SK_ID_CURR)."""
    # Atraso: pagamento efetuado após a data da parcela (> 30 dias)
    df_late = (
        installments.withColumn(
            "days_late", F.col("DAYS_ENTRY_PAYMENT") - F.col("DAYS_INSTALMENT")
        )
        .withColumn("has_late_payment", F.when(F.col("days_late") > 30, 1).otherwise(0))
        .groupBy("SK_ID_CURR")
        .agg(F.sum("has_late_payment").alias("total_late_payments"))
    )

    # Gasto médio de cartão nos últimos 3 meses (MONTHS_BALANCE >= -3 ≈ 90 dias)
    df_spend = (
        credit_card.filter(F.col("MONTHS_BALANCE") >= -3)
        .groupBy("SK_ID_CURR")
        .agg(F.avg("AMT_BALANCE").alias("avg_spend_90d"))
    )

    # Média de EXT_SOURCE ignorando nulos (EDA: EXT_SOURCE_1 com 56% de nulos)
    ext_cols = ["EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3"]
    ext_sum = sum(F.coalesce(F.col(c), F.lit(0.0)) for c in ext_cols)
    ext_cnt = sum(F.when(F.col(c).isNotNull(), 1).otherwise(0) for c in ext_cols)

    # Clipping de renda no P99 (EDA: outliers de até 117M)
    income_p99 = applications.approxQuantile("AMT_INCOME_TOTAL", [0.99], 0.001)[0]

    df_base = applications.select(
        "SK_ID_CURR",
        F.col("TARGET").alias("target"),
        F.least(F.col("AMT_INCOME_TOTAL"), F.lit(income_p99)).alias("income"),
        (F.col("DAYS_BIRTH") / -365).cast("int").alias("age"),
        F.when(ext_cnt > 0, ext_sum / ext_cnt).alias("current_bureau_score"),
    )

    return (
        df_base.join(df_late, "SK_ID_CURR", "left")
        .join(df_spend, "SK_ID_CURR", "left")
        .fillna(0, subset=["total_late_payments", "avg_spend_90d"])
        # score nulo (nenhum EXT_SOURCE) → imputa a mediana global
        .fillna(0.5, subset=["current_bureau_score"])
        .withColumnRenamed("SK_ID_CURR", "client_id")
    )


# COMMAND ----------

# Escrita no Delta Lake (camada Gold)
df_final = generate_credit_features()
df_final.write.format("delta").mode("overwrite").saveAsTable("gold_credit_features")
print(f"gold_credit_features: {df_final.count():,} registros")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exportação para o BigQuery (Feature Store — spec seção 4)

# COMMAND ----------

(
    spark.table("gold_credit_features")
    .write.format("bigquery")
    .option("table", "banco-databricks-ml.credit_risk_features.gold_credit_features")
    .option("temporaryGcsBucket", "fintech-data-raw")
    .mode("overwrite")
    .save()
)
print("Exportado para BigQuery: credit_risk_features.gold_credit_features")

# COMMAND ----------

# Validação: paridade de schema com o contrato da API (src/api/schemas.py)
expected = {"client_id", "income", "age", "avg_spend_90d",
            "total_late_payments", "current_bureau_score", "target"}
actual = set(spark.table("gold_credit_features").columns)
assert actual == expected, f"Schema divergente! {actual ^ expected}"
print("Paridade treino/serving OK")
