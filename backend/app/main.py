from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.database import Base, engine
import app.models  # noqa: F401
from app.routers.analysis import router as analysis_router
from app.routers.auth import router as auth_router
from app.routers.career_profile import router as career_profile_router
from app.routers.dashboard import router as dashboard_router
from app.routers.interviews import router as interviews_router
from app.routers.job_descriptions import router as job_descriptions_router
from app.routers.resumes import router as resumes_router
from app.routers.roadmaps import router as roadmaps_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.project_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(career_profile_router)
app.include_router(resumes_router)
app.include_router(job_descriptions_router)
app.include_router(analysis_router)
app.include_router(roadmaps_router)
app.include_router(interviews_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "career-os-ai-api"}