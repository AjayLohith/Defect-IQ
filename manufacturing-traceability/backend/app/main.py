import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.v1.router import api_router

app = FastAPI(
    title="TraceFlow // Manufacturing Defect-Traceability API",
    description="Deterministic manufacturing defect-traceability, blast-radius isolation, and quality management engine.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health", tags=["System"])
def health_check():
    """System health and deterministic engine environment check."""
    return {
        "status": "healthy",
        "service": "traceflow-api",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "seed": int(os.getenv("GENERATOR_SEED", "20261022")),
        "profile": os.getenv("GENERATOR_PROFILE", "starter"),
    }


# Include all v1 API routes
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
