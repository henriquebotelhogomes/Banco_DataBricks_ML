"""Validação local do modelo (Fase 2, item 5.1 — antes de ativar o trial Databricks).

Replica em pandas a lógica da tabela Gold (notebook 02) e treina o XGBoost
(notebook 03) sobre os CSVs locais, reportando AUC-ROC e KS. Serve para
validar a lógica e antecipar a performance esperada no Databricks.

Execução:  uv run python src/models/train_local.py
"""

from pathlib import Path

import pandas as pd
import xgboost as xgb
from scipy.stats import ks_2samp
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

RAW = Path("data/raw")
FEATURES = ["income", "age", "avg_spend_90d", "total_late_payments", "current_bureau_score"]


def build_gold_features() -> pd.DataFrame:
    """Espelho pandas do notebook 02_feature_engineering (paridade de lógica)."""
    app = pd.read_csv(
        RAW / "application_train.csv",
        usecols=["SK_ID_CURR", "TARGET", "AMT_INCOME_TOTAL", "DAYS_BIRTH",
                 "EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3"],
    )

    inst = pd.read_csv(
        RAW / "installments_payments.csv",
        usecols=["SK_ID_CURR", "DAYS_INSTALMENT", "DAYS_ENTRY_PAYMENT"],
    )
    inst["has_late_payment"] = (
        (inst["DAYS_ENTRY_PAYMENT"] - inst["DAYS_INSTALMENT"]) > 30
    ).astype(int)
    late = inst.groupby("SK_ID_CURR")["has_late_payment"].sum().rename("total_late_payments")

    cc = pd.read_csv(
        RAW / "credit_card_balance.csv",
        usecols=["SK_ID_CURR", "MONTHS_BALANCE", "AMT_BALANCE"],
    )
    spend = (
        cc[cc["MONTHS_BALANCE"] >= -3]
        .groupby("SK_ID_CURR")["AMT_BALANCE"].mean().rename("avg_spend_90d")
    )

    gold = pd.DataFrame(
        {
            "client_id": app["SK_ID_CURR"],
            "target": app["TARGET"],
            # clipping de renda no P99 (EDA: outliers de até 117M)
            "income": app["AMT_INCOME_TOTAL"].clip(upper=app["AMT_INCOME_TOTAL"].quantile(0.99)),
            "age": (app["DAYS_BIRTH"] / -365).astype(int),
            # média de EXT_SOURCE ignorando nulos; sem nenhum score → mediana 0.5
            "current_bureau_score": app[["EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3"]]
            .mean(axis=1)
            .fillna(0.5),
        }
    )
    gold = gold.merge(late, left_on="client_id", right_index=True, how="left")
    gold = gold.merge(spend, left_on="client_id", right_index=True, how="left")
    gold[["total_late_payments", "avg_spend_90d"]] = gold[
        ["total_late_payments", "avg_spend_90d"]
    ].fillna(0)
    return gold


def main() -> None:
    gold = build_gold_features()
    print(f"gold local: {len(gold):,} registros | default: {gold['target'].mean():.2%}")

    X, y = gold[FEATURES], gold["target"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
    model = xgb.XGBClassifier(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=6,
        objective="binary:logistic",
        scale_pos_weight=scale_pos_weight,
        eval_metric="auc",
        early_stopping_rounds=30,
    )
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

    proba = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, proba)
    ks = ks_2samp(proba[y_test == 1], proba[y_test == 0]).statistic * 100

    print(f"\nAUC-ROC = {auc:.4f}  (meta spec: > 0.85 | baseline 5 features)")
    print(f"KS      = {ks:.1f}   (meta spec: > 40)")

    importance = pd.Series(model.feature_importances_, index=FEATURES).sort_values(ascending=False)
    print("\nImportância das features:")
    print(importance.round(3).to_string())


if __name__ == "__main__":
    main()
