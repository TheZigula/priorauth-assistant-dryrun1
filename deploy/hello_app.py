# deploy/hello_app.py: owned by instance 4 (deploy). A placeholder backend that only answers /health, so
# Docker -> GitHub -> App Platform is proven before the real backend exists. Retired at brief step 7.
from fastapi import FastAPI

app = FastAPI(title="priorauth-hello")


@app.get("/health")
def health() -> dict:
    return {"ok": True, "service": "priorauth-hello", "stage": "pipeline proof, not the real backend"}
