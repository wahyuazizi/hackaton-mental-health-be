from pydantic import BaseModel
from typing import List, Dict, Optional

class AssessmentAnswer(BaseModel):
    answers: Dict[str, int]
    timestamp: str

class RiskAssessment(BaseModel):
    level: str
    color: str
    description: str

class AssessmentScore(BaseModel):
    total_score: int
    max_score: int
    percentage: float

class AssessmentResult(BaseModel):
    risk_assessment: RiskAssessment
    score: AssessmentScore
    recommendations: List[str]
    emergency_contacts: Optional[List[str]] = None
