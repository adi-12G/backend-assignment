from fastapi import FastAPI
from sqlalchemy import text
from app.centres import router as centres_router
from app import models
from app.auth import router as auth_router
from app.database import Base, engine
from app.bookings import router as bookings_router
from app.payments import router as payments_router
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="EVE Healthcare API",
    description="Diagnostic test booking and simulated payment service",
    version="1.0.0",
)


app.include_router(auth_router)
app.include_router(centres_router)
app.include_router(bookings_router)
app.include_router(payments_router)

@app.get("/")
def root():
    return {
        "message": "EVE Healthcare API is running"
    }


@app.get("/health")
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected",
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
        }