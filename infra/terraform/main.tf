# Infraestrutura GCP — Fase 1 (spec seção 12)
# Cloud Run será adicionado na Fase 3.
#
# Autenticação para o apply (usuário owner via gcloud):
#   $env:GOOGLE_OAUTH_ACCESS_TOKEN = (gcloud auth print-access-token)
#
# Buckets criados via gcloud na Fase 1 são incorporados ao estado via `terraform import`.

terraform {
  required_version = ">= 1.5"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {
  type    = string
  default = "banco-databricks-ml"
}

variable "region" {
  type    = string
  default = "us-central1"
}

# Artefatos de modelo (model.bst promovido a Production, relatórios Evidently)
resource "google_storage_bucket" "model_artifacts" {
  name                        = "fintech-models-bucket"
  location                    = "US-CENTRAL1"
  uniform_bucket_level_access = true
}

# Dados brutos (CSVs Home Credit — camada Bronze) e remote DVC
resource "google_storage_bucket" "data_raw" {
  name                        = "fintech-data-raw"
  location                    = "US-CENTRAL1"
  uniform_bucket_level_access = true
}

# Repositório Docker da API (usado pelo CI/CD na Fase 3)
resource "google_artifact_registry_repository" "api_repo" {
  repository_id = "credit-api"
  location      = var.region
  format        = "DOCKER"
  description   = "Imagens da Credit Risk Scoring API"
}

# Feature Store (tabela Gold exportada do Databricks + prediction_logs)
resource "google_bigquery_dataset" "feature_store" {
  dataset_id = "credit_risk_features"
  location   = "US"
}

output "artifact_registry_repo" {
  value = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.api_repo.repository_id}"
}
