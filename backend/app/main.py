from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.trips import router as trips_router

app = FastAPI(
    title="Tripwise API",
    version="0.1.0",
    description="AI-powered multi-agent travel planning system",
)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trips_router)


@app.get("/")
def read_root():
    return {
        "message": "Tripwise API is running",
        "version": "0.1.0",
    }


@app.get("/health")
def read_health():
    return {
        "status": "healthy",
    }
