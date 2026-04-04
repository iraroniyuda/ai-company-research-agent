from fastapi import FastAPI

from app.api.routes.companies import router as companies_router
from app.core.database import create_tables

app = FastAPI(title="AI Company Research Agent")

app.include_router(companies_router)


@app.on_event("startup")
def on_startup():
    create_tables()


@app.get("/")
def root():
    return {"message": "AI Company Research Agent is running"}
