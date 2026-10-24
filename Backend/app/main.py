import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from .database import Base, engine
from . import models
from .routers.patients import router as patient_router
from .routers.sessions import router as session_router
from .routers.consents import router as consent_router
from .routers.auth import router as auth_router
from .routers.interviews import router as interview_router
from .routers.answers import router as answer_router
from .routers.questions import router as question_router
from .routers.safety import router as safety_router
from .routers.documents import router as documents_router
from .routers.timeline import router as timeline_router
from .routers.summaries import router as summaries_router
from .routers.doctor_dashboard import router as doctor_dashboard_router
from .routers.fhir import router as fhir_router
from .routers.consultations import router as consultations_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="SIH Project API",
    description="AI-powered digital clinical intake platform",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(patient_router)
app.include_router(session_router)
app.include_router(consent_router)
app.include_router(auth_router)
app.include_router(interview_router)
app.include_router(answer_router)
app.include_router(question_router)
app.include_router(safety_router)
app.include_router(documents_router)
app.include_router(timeline_router)
app.include_router(summaries_router)
app.include_router(doctor_dashboard_router)
app.include_router(fhir_router)
app.include_router(consultations_router)


@app.get("/")
def root():
    return {
        "message": "SIH Project backend is running",
        "ai_enabled": bool(os.getenv("OPENAI_API_KEY")),
        "ai_model": os.getenv(
            "OPENAI_MODEL",
            "gpt-5.6-luna",
        ),
    }