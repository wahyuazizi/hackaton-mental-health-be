from fastapi import APIRouter, HTTPException, Depends
from app.models.assessment import AssessmentAnswer, AssessmentResult
from app.services.assessment_service import AssessmentService
from app.api.dependencies import get_assessment_service

router = APIRouter(prefix="/api/assessment", tags=["assessment"])

@router.get("/questions")
async def get_assessment_questions(
    assessment_service: AssessmentService = Depends(get_assessment_service)
):
    """Get all assessment questions"""
    try:
        questions = assessment_service.get_questions()
        return {"questions": questions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch questions: {str(e)}")

@router.post("/submit", response_model=AssessmentResult)
async def submit_assessment(
    assessment: AssessmentAnswer,
    assessment_service: AssessmentService = Depends(get_assessment_service)
):
    """Submit assessment answers and get results"""
    try:
        result = assessment_service.process_assessment(assessment.answers)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process assessment: {str(e)}")

@router.get("/statistics")
async def get_assessment_statistics():
    """Get assessment statistics (placeholder)"""
    return {
        "total_assessments": 0,
        "risk_distribution": {
            "Rendah": 0,
            "Sedang": 0,
            "Tinggi": 0,
            "Sangat Tinggi": 0
        }
    }