from fastapi import FastAPI, HTTPException, status
from models import WorkoutTelemetryPayload, GeminiWorkoutAnalysisResponse
from services.ai_coach import generate_workout_analysis
import os

app = FastAPI(
    title="FitAI Biomechanics - Cognitive Brain API",
    description="Backend microservice orchestrating Gemini 1.5 Pro with ReAct for sports physiology analysis.",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "FitAI Biomechanics Cognitive Brain is running."}

@app.post(
    "/api/v1/analyze-workout",
    response_model=GeminiWorkoutAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze workout telemetry with Gemini API",
    description="Receives a batch of physiological and biomechanical data from the Android app, runs a ReAct cycle with Gemini 1.5 Pro, and returns a strictly structured JSON response for the next workout plan and technical evaluation."
)
def analyze_workout(payload: WorkoutTelemetryPayload):
    try:
        # Pass the validated payload to the AI service
        analysis = generate_workout_analysis(payload)
        return analysis
    except ValueError as ve:
        # e.g., missing API key or client initialization error
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        # e.g., Gemini API call failed or parsing failed
        raise HTTPException(status_code=502, detail=f"AI Processing Error: {str(e)}")

# To run locally: uvicorn main:app --reload
