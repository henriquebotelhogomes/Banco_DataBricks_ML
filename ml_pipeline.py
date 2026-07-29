"""Orquestração dos Databricks Jobs (Fase 2 — spec 1.3.2).

Cria/atualiza os dois Workflows do projeto via Databricks SDK:
  - credit-risk-training : mensal  (notebooks 01 → 02 → 03)
  - drift-monitoring     : semanal (notebook 04)

Requisitos: DATABRICKS_HOST e DATABRICKS_TOKEN no ambiente (.env, fora do Git).
Execução:   uv run python ml_pipeline.py
"""

import os

from databricks.sdk import WorkspaceClient
from databricks.sdk.service import jobs

REPO_PATH = "/Repos/henriquebotelho1@gmail.com/Banco_DataBricks_ML"
NOTEBOOKS = f"{REPO_PATH}/notebooks/databricks"

# Job cluster mínimo (mais barato que cluster interativo) com auto-termination
JOB_CLUSTER = jobs.JobCluster(
    job_cluster_key="small-job-cluster",
    new_cluster={
        "spark_version": "13.3.x-scala2.12",
        "node_type_id": "e2-standard-4",
        "num_workers": 1,
        "gcp_attributes": {"google_service_account": os.environ.get("GCP_SA_EMAIL", "credit-ai-sa@banco-databricks-ml.iam.gserviceaccount.com")},
    },
)


def notebook_task(key: str, path: str, depends_on: str | None = None) -> jobs.Task:
    return jobs.Task(
        task_key=key,
        notebook_task=jobs.NotebookTask(notebook_path=path),
        job_cluster_key="small-job-cluster",
        depends_on=[jobs.TaskDependency(task_key=depends_on)] if depends_on else None,
    )


def upsert_job(client: WorkspaceClient, name: str, tasks: list, cron: str) -> None:
    settings = dict(
        name=name,
        tasks=tasks,
        job_clusters=[JOB_CLUSTER],
        schedule=jobs.CronSchedule(
            quartz_cron_expression=cron, timezone_id="America/Sao_Paulo"
        ),
        max_concurrent_runs=1,
    )
    existing = [j for j in client.jobs.list(name=name)]
    if existing:
        client.jobs.reset(job_id=existing[0].job_id, new_settings=jobs.JobSettings(**settings))
        print(f"Job atualizado: {name} (id={existing[0].job_id})")
    else:
        created = client.jobs.create(**settings)
        print(f"Job criado: {name} (id={created.job_id})")


def main() -> None:
    client = WorkspaceClient()  # usa DATABRICKS_HOST/TOKEN do ambiente

    # Treinamento mensal: ingestão -> features -> treino/promoção
    upsert_job(
        client,
        name="credit-risk-training",
        tasks=[
            notebook_task("bronze_ingestion", f"{NOTEBOOKS}/01_bronze_ingestion"),
            notebook_task("feature_engineering", f"{NOTEBOOKS}/02_feature_engineering", "bronze_ingestion"),
            notebook_task("train_model", f"{NOTEBOOKS}/03_train_model", "feature_engineering"),
        ],
        cron="0 0 3 1 * ?",  # dia 1 de cada mês, 03:00
    )

    # Drift semanal
    upsert_job(
        client,
        name="drift-monitoring",
        tasks=[notebook_task("drift_monitoring", f"{NOTEBOOKS}/04_drift_monitoring")],
        cron="0 0 4 ? * MON",  # toda segunda, 04:00
    )


if __name__ == "__main__":
    main()
