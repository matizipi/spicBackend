import os
from google import genai
from google.genai import types
from models import WorkoutTelemetryPayload, GeminiWorkoutAnalysisResponse

# Initialize the Gemini client. It will automatically look for the GEMINI_API_KEY environment variable.
# For local testing if the key is missing, you'll need to set it before running the server.
# Example: export GEMINI_API_KEY="your_key"
try:
    client = genai.Client()
except Exception as e:
    print(f"Warning: Gemini client initialization failed. Ensure GEMINI_API_KEY is set. Error: {e}")
    client = None

def generate_workout_analysis(payload: WorkoutTelemetryPayload) -> GeminiWorkoutAnalysisResponse:
    if client is None:
        raise ValueError("Gemini client is not initialized. Check your GEMINI_API_KEY.")

    # Calculate some summary stats to feed the LLM instead of raw huge arrays
    avg_cadence = sum(l.cadenceSpm for l in payload.logs if l.cadenceSpm) / max(1, len([l for l in payload.logs if l.cadenceSpm]))
    avg_impact = sum(l.impactForceG for l in payload.logs if l.impactForceG) / max(1, len([l for l in payload.logs if l.impactForceG]))
    avg_hr = sum(l.heartRateBpm for l in payload.logs if l.heartRateBpm) / max(1, len([l for l in payload.logs if l.heartRateBpm]))

    data_summary = f"""
    --- Datos del Entrenamiento ---
    Actividad: {payload.session.activityType}
    Distancia: {payload.session.totalDistanceMeters} metros
    Duración: {payload.session.durationSeconds} segundos
    TRIMP Acumulado de la sesión: {payload.session.trimpAccumulated}
    Estado de Forma (TSB) Inicial: {payload.session.initialTsbState}
    Estrés Percibido: {payload.session.qualitativeStress or 'No reportado'}
    Fase Menstrual: {payload.session.qualitativeMenstrualPhase or 'No aplicable/No reportado'}
    
    --- Resumen Biomecánico y Fisiológico ---
    Cadencia Promedio: {avg_cadence:.1f} SPM
    Fuerza de Impacto Promedio: {avg_impact:.2f} G
    Frecuencia Cardíaca Promedio: {avg_hr:.1f} BPM
    """

    system_instruction = """
    Eres el 'Cerebro Cognitivo' de una plataforma de entrenamiento biomecánico y fisiológico avanzado.
    Tu objetivo es actuar como un Fisiólogo Jefe y Entrenador de Élite.
    
    Se te proporcionarán los datos de telemetría de la última sesión de entrenamiento de un atleta, incluyendo su Estado de Forma (TSB) y métricas biomecánicas (Cadencia, Impacto).
    
    DEBES utilizar el siguiente marco de razonamiento (ReAct) internamente antes de generar tu respuesta estructurada:
    1. OBSERVE: Analiza el TSB (si es < -10 hay fatiga, si es > 10 está fresco), la cadencia (ideal ~170-180 SPM), y el impacto (menor impacto es mejor técnica).
    2. THINK: Relaciona la fatiga con las métricas biomecánicas. ¿El impacto subió por fatiga muscular? ¿Qué necesita el atleta ahora (recuperación o intensidad)?
    3. ACT: Define la evaluación biomecánica, el diagnóstico de fatiga, el tiempo de recuperación, y diseña el PRÓXIMO entrenamiento estructurado.
    
    Devuelve la salida ESTRICTAMENTE según el JSON Schema requerido. Mantén las evaluaciones concisas, directas y motivadoras.
    """

    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=data_summary,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=GeminiWorkoutAnalysisResponse,
                temperature=0.2, # Low temperature for more analytical/consistent coaching
            )
        )
        
        # Pydantic parsing of the JSON response
        return GeminiWorkoutAnalysisResponse.parse_raw(response.text)
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        raise e

def generate_global_coach_suggestion(payload: 'WorkoutHistoryPayload') -> 'GlobalCoachSuggestion':
    if client is None:
        raise ValueError("Gemini client is not initialized. Check your GEMINI_API_KEY.")
        
    from models import GlobalCoachSuggestion

    # Build a text summary of the sessions
    history_text = "--- Historial Reciente (Orden cronológico) ---\n"
    for i, s in enumerate(payload.sessions):
        history_text += f"Sesión {i+1}: {s.activityType}, {s.totalDistanceMeters}m, TRIMP: {s.trimpAccumulated}\n"
        if s.aiBiomechanicsFeedback:
            history_text += f"   Feedback previo: {s.aiBiomechanicsFeedback}\n"

    system_instruction = """
    Eres el 'Cerebro Cognitivo' y Entrenador de Élite de FitAI.
    Tu objetivo es analizar el historial reciente de entrenamientos del atleta y decidir cuál debería ser su siguiente paso HOY.
    
    Analiza la acumulación de TRIMP (carga de entrenamiento) y los tipos de actividad.
    Si el atleta ha entrenado muchos días seguidos o tiene TRIMP muy alto, sugiere 'Descanso' o 'Recuperación'.
    Si el atleta lleva un ritmo estable, sugiere un 'Nuevo Desafío' o 'Progresión'.
    Si el historial muestra pocas sesiones recientes o de muy baja intensidad, sugiere 'Aumentar volumen'.
    
    Devuelve la salida ESTRICTAMENTE según el JSON Schema de GlobalCoachSuggestion.
    Sé motivador, conciso y profesional.
    """

    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=history_text,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=GlobalCoachSuggestion,
                temperature=0.3,
            )
        )
        return GlobalCoachSuggestion.parse_raw(response.text)
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        raise e
