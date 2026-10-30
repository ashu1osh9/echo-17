# One-origin RF + Gemma research demo; no restricted TabPFN payload is accepted.
FROM node:22.17.0-bookworm-slim AS frontend
WORKDIR /src/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.11.5-slim-bookworm
WORKDIR /app/backend
COPY backend/requirements-demo.txt ./
RUN pip install --no-cache-dir -r requirements-demo.txt
COPY backend/app ./app
COPY backend/ml ./ml
COPY LICENSE /app/LICENSE
COPY THIRD_PARTY_NOTICES.md /app/THIRD_PARTY_NOTICES.md
ARG ECHO_BUNDLE_URL
ARG ECHO_BUNDLE_SHA256
ENV ECHO_DATA_ROOT=/app/runtime/demo-data ECHO_REPORT_MODE=precomputed ECHO_PUBLIC_MODEL_POLICY=rf_only ECHO_STATIC_DIR=/app/frontend/dist OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
RUN python -m ml.install_demo
COPY --from=frontend /src/frontend/dist /app/frontend/dist
USER 10001:10001
EXPOSE 8000
CMD ["sh", "-c", "exec python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
