# Dockerfile: owned by instance 4 (deploy). The backend image: pinned Python slim base, non-root user,
# uvicorn on port 8080, /health as the container health check. PHASE 1: serves the deploy/ placeholder.
FROM python:3.13.15-slim-trixie@sha256:7c61056e61ac89e852de05f3dc6fa51a6dd2181797bceed46aa725dd7cb2cd3b

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    ANONYMIZED_TELEMETRY=False \
    LANGSMITH_TRACING=false \
    LANGCHAIN_TRACING_V2=false

# Non-root user. It owns /app so the app can write its local state (vector store, thread state, submissions log).
RUN useradd --create-home --uid 10001 app
WORKDIR /app
RUN chown app:app /app

# PHASE 1 (pipeline proof): only what the placeholder needs, pinned to the versions installed on this box.
# PHASE 2 (brief step 7) swaps these two lines for requirements.txt, backend/ and data/, and the CMD module.
RUN pip install fastapi==0.128.2 uvicorn==0.40.0
COPY --chown=app:app deploy/hello_app.py ./deploy/hello_app.py

USER app
EXPOSE 8080
HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=2)"]
# One process on purpose: the approval pause and the per-thread memory live in this process and its SQLite file.
CMD ["python", "-m", "uvicorn", "deploy.hello_app:app", "--host", "0.0.0.0", "--port", "8080"]
