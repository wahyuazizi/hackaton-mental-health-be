from typing import List, Optional
from app.models.assessment import RiskAssessment, AssessmentScore, AssessmentResult
from app.core.constants import ASSESSMENT_QUESTIONS, CRISIS_RESOURCES
from app.core.exceptions import AssessmentException
import logging

logger = logging.getLogger(__name__)

class AssessmentService:
    @staticmethod
    def get_questions():
        """Get all assessment questions"""
        return ASSESSMENT_QUESTIONS
    
    @staticmethod
    def calculate_risk_assessment(total_score: int, max_score: int) -> RiskAssessment:
        """Calculate risk assessment based on total score"""
        try:
            percentage = (total_score / max_score) * 100 if max_score > 0 else 0
            
            if percentage <= 25:
                return RiskAssessment(
                    level="Rendah",
                    color="emerald",
                    description="Risiko rendah kecanduan judi"
                )
            elif percentage <= 50:
                return RiskAssessment(
                    level="Sedang",
                    color="yellow",
                    description="Risiko sedang - perlu perhatian"
                )
            elif percentage <= 75:
                return RiskAssessment(
                    level="Tinggi",
                    color="orange",
                    description="Risiko tinggi - perlu bantuan profesional"
                )
            else:
                return RiskAssessment(
                    level="Sangat Tinggi",
                    color="red",
                    description="Risiko sangat tinggi - segera cari bantuan"
                )
        except Exception as e:
            logger.error(f"Error calculating risk assessment: {str(e)}")
            raise AssessmentException(f"Failed to calculate risk assessment: {str(e)}")
    
    @staticmethod
    def get_recommendations(risk_level: str) -> List[str]:
        """Get recommendations based on risk level"""
        recommendations = {
            "Rendah": [
                "✅ Pertahankan kebiasaan judi yang terkontrol",
                "✅ Tetap awasi pengeluaran dan waktu yang dihabiskan",
                "✅ Gunakan fitur AI Counselor untuk tips pencegahan"
            ],
            "Sedang": [
                "⚠️ Mulai batasi waktu dan uang untuk judi",
                "⚠️ Gunakan fitur AI Counselor untuk strategi coping",
                "⚠️ Pertimbangkan untuk berbicara dengan keluarga atau teman",
                "⚠️ Monitor perilaku judi Anda secara teratur"
            ],
            "Tinggi": [
                "🚨 Segera cari bantuan dari profesional kesehatan mental",
                "🚨 Gunakan AI Counselor untuk dukungan darurat",
                "🚨 Pertimbangkan untuk bergabung dengan support group",
                "🚨 Blokir akses ke situs judi online",
                "🚨 Minta dukungan keluarga dan teman terdekat"
            ],
            "Sangat Tinggi": [
                "🚨 Segera cari bantuan dari profesional kesehatan mental",
                "🚨 Gunakan AI Counselor untuk dukungan darurat",
                "🚨 Pertimbangkan untuk bergabung dengan support group",
                "🚨 Blokir akses ke situs judi online",
                "🚨 Minta dukungan keluarga dan teman terdekat",
                "🚨 Hubungi hotline darurat jika merasa tidak aman"
            ]
        }
        return recommendations.get(risk_level, [])
    
    @staticmethod
    def get_emergency_contacts(risk_level: str) -> Optional[List[str]]:
        """Get emergency contacts for high-risk users"""
        if risk_level in ["Tinggi", "Sangat Tinggi"]:
            return CRISIS_RESOURCES
        return None
    
    @staticmethod
    def process_assessment(answers: dict) -> AssessmentResult:
        """Process assessment answers and return results"""
        try:
            # Calculate total possible score
            max_score = sum(len(category["questions"]) for category in ASSESSMENT_QUESTIONS) * 3
            
            # Calculate user's total score
            total_score = sum(answers.values())
            
            # Calculate percentage
            percentage = (total_score / max_score) * 100 if max_score > 0 else 0
            
            # Get risk assessment
            risk_assessment = AssessmentService.calculate_risk_assessment(total_score, max_score)
            
            # Get recommendations
            recommendations = AssessmentService.get_recommendations(risk_assessment.level)
            
            # Get emergency contacts if needed
            emergency_contacts = AssessmentService.get_emergency_contacts(risk_assessment.level)
            
            # Create score object
            score = AssessmentScore(
                total_score=total_score,
                max_score=max_score,
                percentage=round(percentage, 2)
            )
            
            result = AssessmentResult(
                risk_assessment=risk_assessment,
                score=score,
                recommendations=recommendations,
                emergency_contacts=emergency_contacts
            )
            
            logger.info(f"Assessment completed - Risk Level: {risk_assessment.level}, Score: {total_score}/{max_score}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing assessment: {str(e)}")
            raise AssessmentException(f"Failed to process assessment: {str(e)}")
