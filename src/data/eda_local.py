"""EDA local (Fase 0, item 3.3) — validação das colunas mapeadas na spec 3.3.

Objetivo: confirmar que as colunas usadas no feature engineering (spec seção 7)
existem e têm o comportamento esperado, usando amostras (nrows) para não
estourar memória local. A exploração completa acontecerá no Databricks (Fase 2).

Execução:  uv run python src/data/eda_local.py
"""

from pathlib import Path

import pandas as pd

RAW = Path("data/raw")
SAMPLE = 100_000


def section(title: str) -> None:
    print(f"\n{'=' * 70}\n{title}\n{'=' * 70}")


def main() -> None:
    # ------------------------------------------------------------------
    section("1. application_train — base principal (TARGET, income, age, EXT_SOURCE)")
    cols = [
        "SK_ID_CURR", "TARGET", "AMT_INCOME_TOTAL", "DAYS_BIRTH",
        "EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3",
    ]
    app = pd.read_csv(RAW / "application_train.csv", usecols=cols)
    print(f"registros: {len(app):,}")
    print(f"taxa de default (TARGET=1): {app['TARGET'].mean():.2%}")
    print(f"income  → min={app['AMT_INCOME_TOTAL'].min():,.0f} "
          f"mediana={app['AMT_INCOME_TOTAL'].median():,.0f} "
          f"max={app['AMT_INCOME_TOTAL'].max():,.0f}")
    age = (app["DAYS_BIRTH"] / -365).astype(int)
    print(f"age     → min={age.min()} mediana={int(age.median())} max={age.max()}")
    ext_mean = app[["EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3"]].mean(axis=1)
    print(f"bureau_score (média EXT_SOURCE) → min={ext_mean.min():.3f} "
          f"mediana={ext_mean.median():.3f} max={ext_mean.max():.3f}")
    print("nulos EXT_SOURCE (%):")
    print((app[["EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3"]]
           .isna().mean() * 100).round(1).to_string())

    # ------------------------------------------------------------------
    section(f"2. installments_payments (amostra {SAMPLE:,}) — days_late")
    inst = pd.read_csv(
        RAW / "installments_payments.csv",
        usecols=["SK_ID_CURR", "DAYS_INSTALMENT", "DAYS_ENTRY_PAYMENT"],
        nrows=SAMPLE,
    )
    days_late = inst["DAYS_ENTRY_PAYMENT"] - inst["DAYS_INSTALMENT"]
    print(f"days_late → min={days_late.min():.0f} mediana={days_late.median():.0f} "
          f"max={days_late.max():.0f}")
    print(f"parcelas com atraso > 30 dias: {(days_late > 30).mean():.2%}")

    # ------------------------------------------------------------------
    section(f"3. credit_card_balance (amostra {SAMPLE:,}) — avg_spend_90d")
    cc = pd.read_csv(
        RAW / "credit_card_balance.csv",
        usecols=["SK_ID_CURR", "MONTHS_BALANCE", "AMT_BALANCE"],
        nrows=SAMPLE,
    )
    recent = cc[cc["MONTHS_BALANCE"] >= -3]
    print(f"registros na janela de 3 meses: {len(recent):,} de {len(cc):,}")
    print(f"AMT_BALANCE → mediana={recent['AMT_BALANCE'].median():,.0f} "
          f"max={recent['AMT_BALANCE'].max():,.0f}")

    # ------------------------------------------------------------------
    section("4. Conclusão — mapeamento spec 3.3")
    print("""
    SK_ID_CURR                        → client_id             OK
    AMT_INCOME_TOTAL                  → income                OK
    DAYS_BIRTH / -365                 → age                   OK
    DAYS_ENTRY_PAYMENT-DAYS_INSTALMENT→ days_late (>30)       OK
    AMT_BALANCE (MONTHS_BALANCE>=-3)  → avg_spend_90d         OK
    média EXT_SOURCE_1/2/3            → current_bureau_score  OK (atenção a nulos)
    TARGET                            → target                OK (~8% default)
    """)


if __name__ == "__main__":
    main()
