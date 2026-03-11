"""BizHub FastAPI Application — REST API backend.

Run with:
    python bizhub.py --api
    # or directly:
    uvicorn src.api.main:app --reload
"""
import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import inventory, sales, contacts, leads, dashboard, auth, hr, settings

logger = logging.getLogger(__name__)

app = FastAPI(
    title="BizHub API",
    version="4.0.0",
    description="BizHub ERP REST API — connects desktop data to web frontend",
)

# Allow all origins for development; restrict in production via env vars
ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
app.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
app.include_router(sales.router, prefix="/sales", tags=["sales"])
app.include_router(contacts.router, prefix="/contacts", tags=["contacts"])
app.include_router(leads.router, prefix="/leads", tags=["leads"])
app.include_router(hr.router, prefix="/hr", tags=["hr"])
app.include_router(settings.router, prefix="/settings", tags=["settings"])


@app.get("/", tags=["root"])
def root():
    """Health check endpoint."""
    return {"status": "ok", "app": "BizHub API", "version": "4.0.0"}


@app.get("/health", tags=["root"])
def health():
    """Health check."""
    return {"status": "healthy"}
