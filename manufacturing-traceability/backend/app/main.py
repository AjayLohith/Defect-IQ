import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Manufacturing Defect-Traceability API",
    description="Deterministic manufacturing defect-traceability and quality management system.",
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
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "traceflow-api",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "seed": int(os.getenv("GENERATOR_SEED", "20261022")),
        "profile": os.getenv("GENERATOR_PROFILE", "starter"),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)

