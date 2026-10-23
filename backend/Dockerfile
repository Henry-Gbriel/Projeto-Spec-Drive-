# Imagem da API pública (FastAPI). Usada no Google Cloud Run (plan.md, "Publicação").
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv

COPY --from=ghcr.io/astral-sh/uv:0.8 /uv /usr/local/bin/uv

WORKDIR /app
# Dependências primeiro, para aproveitar o cache de camadas.
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project
COPY src ./src
COPY README.md ./
RUN uv sync --locked --no-dev

# O catálogo fica fora de backend/; a API não precisa dele (lê tudo do banco).
RUN useradd --create-home --uid 10001 observatorio
USER observatorio

ENV PATH="/app/.venv/bin:$PATH" \
    AMBIENTE=producao \
    PORT=8080
EXPOSE 8080
CMD ["sh", "-c", "uvicorn observatorio.api.app:app --host 0.0.0.0 --port ${PORT} --proxy-headers --forwarded-allow-ips='*'"]
