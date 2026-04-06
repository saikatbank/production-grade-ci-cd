from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from app.api.routes import router as api_router
from app.api.health import router as health_router
from app.db.database import engine
from app.db import models
from app.core.config import settings

# Create database tables only if not in testing environment
if not os.environ.get("TESTING"):
    try:
        models.Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Warning: Could not connect to database at startup. {e}")

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(api_router, prefix="/api/v1")
app.include_router(health_router, prefix="/health")

# Ensure the static directory exists
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def read_root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))
