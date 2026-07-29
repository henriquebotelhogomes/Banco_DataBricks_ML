# Dockerfile — Credit Risk Scoring API (spec seção 13)
FROM python:3.11-slim

# uv para instalação determinística das dependências (pyproject.toml + uv.lock)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY src/ ./src/

# O modelo NÃO é embutido na imagem: é carregado de
# gs://fintech-models-bucket/v1/model.bst no startup da aplicação (Fase 3)

EXPOSE 8080

CMD ["uv", "run", "--no-sync", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
