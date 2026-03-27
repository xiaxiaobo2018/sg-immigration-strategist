from pathlib import Path

from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv(Path(__file__).resolve().parent / ".env")

try:
    from .routes.analyze import router as analyze_router
except ImportError:
    from routes.analyze import router as analyze_router


app = FastAPI(
    title="SG Immigration Strategist API",
    version="0.1.0",
    description="Backend API for Singapore PR and citizenship readiness analysis.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router)


@app.get("/")
def healthcheck() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "sg-immigration-strategist",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return healthcheck()
