from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.limiter import limiter
from app.routers import recipes, scrape, search, tags, cook_logs, images, shopping


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="NyamNyamBook v2 API",
    version="1.0.0",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS 설정
if settings.ENVIRONMENT == "production":
    origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
else:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}


app.include_router(recipes.router, prefix="/recipes", tags=["recipes"])
app.include_router(scrape.router, prefix="/scrape", tags=["scrape"])
app.include_router(search.router, prefix="/search", tags=["search"])
app.include_router(tags.router, prefix="/tags", tags=["tags"])
app.include_router(cook_logs.router, prefix="/recipes", tags=["cook_logs"])
app.include_router(images.router, prefix="/images", tags=["images"])
app.include_router(shopping.router, prefix="/shopping", tags=["shopping"])
