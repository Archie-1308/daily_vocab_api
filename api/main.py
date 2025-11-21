from fastapi import FastAPI, HTTPException 
from app.schemas import WordResponse
from app.routers import words
from app.routers import practice

from app.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware 

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Vocabulary Practice API",
    version="1.0.0",
    description="API for vocabulary practice and learning"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import Request
from fastapi.responses import JSONResponse

@app.middleware("http")
async def log_exceptions(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.exception(f"Exception during request {request.url.path}: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


# Include routers 
app.include_router(words.router, prefix="/api", tags=["words"])
app.include_router(practice.router, prefix="/api", tags=["practice"])   


@app.get("/")
def read_root():
    return {
        "message": "Vocabulary Practice API",
        "version": "1.0.0",
        "endpoints": {
            "random_word": "/api/word",
            "validate": "/api/validate-sentence",
            "summary": "/api/summary",
            "history": "/api/history"
        }
    }