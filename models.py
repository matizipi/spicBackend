from pydantic import BaseModel, Field
from typing import List, Optional

# --- Input Models (Request from Android) ---

class SensorDataPoint(BaseModel):
    timestamp: int
    cadenceSpm: Optional[int] = Field(None, ge=0, le=300)
    impactForceG: Optional[float] = Field(None, ge=0.0, le=50.0)
    heartRateBpm: Optional[int] = Field(None, ge=30, le=250)

class WorkoutSessionData(BaseModel):
    activityType: str
    totalDistanceMeters: float = Field(..., ge=0.0)
    durationSeconds: int = Field(..., gt=0)
    trimpAccumulated: float = Field(..., ge=0.0)
    initialTsbState: float
    qualitativeStress: Optional[str] = None
    qualitativeMenstrualPhase: Optional[str] = None

class WorkoutTelemetryPayload(BaseModel):
    session: WorkoutSessionData
    logs: List[SensorDataPoint] = Field(..., max_length=15000, description="Evita ataques DoS por payloads masivos")

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

class SyncWorkoutSession(BaseModel):
    localId: int
    startTimestamp: int
    endTimestamp: Optional[int] = None
    activityType: str
    totalDistanceMeters: float
    trimpAccumulated: float
    aiBiomechanicsFeedback: Optional[str] = None

class SyncPayload(BaseModel):
    sessions: List[SyncWorkoutSession]

class WorkoutHistoryPayload(BaseModel):
    sessions: List[SyncWorkoutSession]

class GlobalCoachSuggestion(BaseModel):
    type: str = Field(description="Categoría principal (ej: Descanso, Repetir, Nuevo Desafío)")
    title: str = Field(description="Título corto de la sugerencia (ej: Día de Recuperación Activa)")
    description: str = Field(description="Descripción detallada de la sugerencia y el motivo, basada en la fatiga y el historial reciente.")
    targetActivity: Optional[str] = Field(description="Si sugiere actividad, cuál (ej: Ciclismo suave).", default=None)
    targetDurationMinutes: Optional[int] = Field(description="Duración sugerida en minutos.", default=None)

# --- User Profile Models ---
class UserProfile(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
