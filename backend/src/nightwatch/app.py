from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from nightwatch.config import get_settings
from nightwatch.db.database import init_db
from nightwatch.webhooks.alertmanager import router as alertmanager_router 
from nightwatch.webhooks.approvals import router as approvals_router 

settings = get_settings()

app = FastAPI(
    title="Nightwatch SRE Agent API",
    description="Autonomous virtual SRE monitoring and incident response team powered by Agno.",
    version="0.1.0",
)

# Enable CORS for the React + Vite frontend dashboard (port 3001)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB on startup
init_db()

# Register routes
app.include_router(alertmanager_router)
app.include_router(approvals_router)


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpooint for container orchestrators and monitoring."""
    return {
        "status": "healthy",
        "app_env": settings.app_env,
        "default_model": settings.default_model,
        "prometheus_url": settings.prometheus_url,
        "loki_url": settings.loki_url,
        "database_url": settings.database_url,
    }
    

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run("nightwatch.app:app", port=7777, reload=True, host="0.0.0.0")