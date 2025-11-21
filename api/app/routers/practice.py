from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
import traceback

from app.database import get_db
from app.models import Word, PracticeSession
from app.schemas import ValidateSentenceRequest, ValidateSentenceResponse
from app.utils import mock_ai_validation

# Define the router
router = APIRouter()


@router.post("/validate-sentence", response_model=ValidateSentenceResponse)
def validate_sentence(
    request: ValidateSentenceRequest,
    db: Session = Depends(get_db)
):
    """
    Receive user sentence, validate using mock AI, save results to DB,
    and return response with score, level, suggestion, corrected sentence.
    """
    try:
        # 1️⃣ Fetch word from DB
        word = db.query(Word).filter(Word.id == request.word_id).first()
        if not word:
            raise HTTPException(status_code=404, detail="Word not found")

        # 2️⃣ Call mock AI validation (correct positional arguments)
        ai_result = mock_ai_validation(
            request.sentence,      # sentence
            word.word,             # target_word
            word.difficulty_level  # difficulty
        )

        score = ai_result["score"]
        level = ai_result["level"]
        suggestion = ai_result["suggestion"]
        corrected_sentence = ai_result["corrected_sentence"]

        # 3️⃣ Save practice session to DB
        session_obj = PracticeSession(
            word_id=word.id,
            user_sentence=request.sentence,
            score=score,           # Decimal in DB
            feedback=suggestion,
            corrected_sentence=corrected_sentence
        )
        db.add(session_obj)
        db.commit()
        db.refresh(session_obj)

        # 4️⃣ Return proper response (convert Decimal → float)
        return ValidateSentenceResponse(
            score=float(session_obj.score),
            level=level,
            suggestion=session_obj.feedback,
            corrected_sentence=session_obj.corrected_sentence
        )

    except Exception as e:
        # Print full traceback for debugging
        traceback_str = traceback.format_exc()
        print("=== ERROR TRACE ===")
        print(traceback_str)

        # Return JSON error for client
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "trace": traceback_str}
        )
