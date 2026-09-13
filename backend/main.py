"""ProcureLens API entrypoint.

Run with:
    uvicorn main:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import analyze, cases, overview, tenders, vendors
from models import orm  # noqa: F401  (registers models on Base.metadata)

app = FastAPI(
    title="ProcureLens API",
    description=(
        "Procurement anomaly-detection and investigation-support API. "
        "Surfaces investigation signals and priority cases for human review -- "
        "it does not determine wrongdoing."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


app.include_router(overview.router)
app.include_router(tenders.router)
app.include_router(vendors.router)
app.include_router(cases.router)
app.include_router(analyze.router)
