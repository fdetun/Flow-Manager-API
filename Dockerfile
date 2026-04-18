# ── Stage 1: builder ─────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: dev ─────────────────────────────────────────────────────────────
FROM python:3.12-slim AS dev

WORKDIR /app

COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt & \
    apt-get update && apt-get install -y make & \
    apt-get update && apt-get install -y git


CMD ["sleep", "infinity"]


# ── Stage 3: runtime ─────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

# Packages only — no pip, no build cache
COPY --from=builder /install /usr/local

# Application source
COPY --chown=appuser:appgroup main.py .
COPY --chown=appuser:appgroup app/ ./app/

USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
