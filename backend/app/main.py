from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

from app.config import settings
from app.database import init_db
from app.routers import auth, jobs, candidates, matches, actions, analytics, search


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables
    await init_db()
    yield
    # Shutdown: cleanup if needed


app = FastAPI(
    title="TalentHunt — AI Candidate Rediscovery",
    description="AI-powered candidate rediscovery system for staffing & recruiting companies.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware (simple in-memory)
request_counts: dict = {}


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    now = time.time()
    window = 60  # 1 minute
    max_requests = 100

    if client_ip not in request_counts:
        request_counts[client_ip] = []

    request_counts[client_ip] = [t for t in request_counts[client_ip] if now - t < window]

    if len(request_counts[client_ip]) >= max_requests:
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded. Try again later."})

    request_counts[client_ip].append(now)
    response = await call_next(request)
    return response


# Register routers
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(jobs.router, prefix=settings.API_PREFIX)
app.include_router(candidates.router, prefix=settings.API_PREFIX)
app.include_router(matches.router, prefix=settings.API_PREFIX)
app.include_router(actions.router, prefix=settings.API_PREFIX)
app.include_router(analytics.router, prefix=settings.API_PREFIX)
app.include_router(search.router, prefix=settings.API_PREFIX)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/")
async def root():
    return {
        "app": "TalentHunt",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }
