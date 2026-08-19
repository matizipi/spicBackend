import os
import requests
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv
from models import WorkoutTelemetryPayload, GeminiWorkoutAnalysisResponse, GlobalCoachSuggestion

load_dotenv()

# Configuración de Groq
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-20b")

# Configuración de Gemini
try:
    gemini_client = genai.Client()
except Exception as e:
    print(f"Warning: Gemini client initialization failed. Ensure GEMINI_API_KEY is set. Error: {e}")
    gemini_client = None

def _call_gemini(prompt: str, system: str, schema_class):
    if gemini_client is None:
        raise ValueError("Gemini client is not initialized. Check your GEMINI_API_KEY.")
    try:
        response = gemini_client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system,
                response_mime_type="application/json",
                response_schema=schema_class,
                temperature=0.2,
            )
        )
        return schema_class.parse_raw(response.text)
    except Exception as e:
        print(f"Error llamando a Gemini API: {e}")
        raise e

def _call_groq(prompt: str, system: str, schema_class):
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY no está configurada. Debes configurar la variable de entorno.")

    url = "https://api.groq.com/openai/v1/chat/completions"
    schema_json = schema_class.schema_json()
    full_prompt = f"{prompt}\n\nIMPORTANTE: Responde ÚNICAMENTE con un objeto JSON válido que respete exactamente este esquema: {schema_json}"
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": full_prompt}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.2
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result_json = response.json()
        response_text = result_json["choices"][0]["message"]["content"]
        return schema_class.parse_raw(response_text)
    except Exception as e:
        print(f"Error llamando a Groq API: {e}")
        raise e

def generate_workout_analysis(payload: WorkoutTelemetryPayload) -> GeminiWorkoutAnalysisResponse:
    # TAREA 1: Análisis Post-Entrenamiento denso -> GEMINI
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
    
    Mantén las evaluaciones concisas, directas y motivadoras.
    """

    return _call_gemini(data_summary, system_instruction, GeminiWorkoutAnalysisResponse)

def generate_global_coach_suggestion(payload: 'WorkoutHistoryPayload') -> 'GlobalCoachSuggestion':
    # TAREA 2: Análisis Rápido del Historial para Dashboard -> GROQ (Llama 3.1)
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
    
    Sé motivador, conciso y profesional.
    """

    return _call_groq(history_text, system_instruction, GlobalCoachSuggestion)
