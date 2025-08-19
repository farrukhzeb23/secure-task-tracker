from fastapi import FastAPI
from app.api.v1.endpoints import users, auth
from app.core.config import settings

app = FastAPI(title=settings.APP_NAME)
app.include_router(users.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")


@app.get('/health')
def health_check():
    return {
        "status": "healthy",
        "message": "Service is running",
        "app_name": settings.APP_NAME
    }
