from pydantic import BaseModel, Field
from typing import List, Optional

# --- Input Models (Request from Android) ---

class SensorDataPoint(BaseModel):
    timestamp: int
    cadenceSpm: Optional[int] = None
    impactForceG: Optional[float] = None
    heartRateBpm: Optional[int] = None

class WorkoutSessionData(BaseModel):
    activityType: str
    totalDistanceMeters: float
    durationSeconds: int
    trimpAccumulated: float
    initialTsbState: float
    qualitativeStress: Optional[str] = None
    qualitativeMenstrualPhase: Optional[str] = None

class WorkoutTelemetryPayload(BaseModel):
    session: WorkoutSessionData
    logs: List[SensorDataPoint]

# --- Output Models (Structured Output for Gemini) ---

class NextWorkoutPlan(BaseModel):
    type: str = Field(description="Tipo de entrenamiento recomendado (ej: Recuperación activa, Series largas, Fondo)")
    durationMinutes: int = Field(description="Duración recomendada en minutos")
    targetHeartRateZone: str = Field(description="Zona cardíaca objetivo recomendada (1 a 5)")
    reasoning: str = Field(description="Breve justificación de la recomendación")

class GeminiWorkoutAnalysisResponse(BaseModel):
    technical_evaluation: str = Field(description="Evaluación biomecánica concisa basada en cadencia e impacto.")
    fatigue_status: str = Field(description="Diagnóstico del estado de fatiga basado en TSB y TRIMP.")
    recommended_recovery_hours: int = Field(description="Horas de recuperación recomendadas.")
    next_workout_plan: NextWorkoutPlan
