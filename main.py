from fastapi import FastAPI, HTTPException, status, Depends
from models import WorkoutTelemetryPayload, GeminiWorkoutAnalysisResponse, SyncPayload
from services.ai_coach import generate_workout_analysis
import os
from database import get_database, close_database_connection
from auth import init_firebase, verify_token

app = FastAPI(
    title="FitAI Biomechanics - Cognitive Brain API",
    description="Backend microservice orchestrating Gemini 1.5 Pro with ReAct for sports physiology analysis.",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_db_client():
    init_firebase()
    get_database()

@app.on_event("shutdown")
async def shutdown_db_client():
    close_database_connection()

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

@app.post("/api/v1/sync", status_code=status.HTTP_200_OK)
async def sync_workouts(payload: SyncPayload, uid: str = Depends(verify_token)):
    db = get_database()
    collection = db["workouts"]
    
    saved_count = 0
    for session in payload.sessions:
        doc = session.dict()
        doc["userId"] = uid
        # Upsert based on userId and localId
        await collection.update_one(
            {"userId": uid, "localId": session.localId},
            {"$set": doc},
            upsert=True
        )
        saved_count += 1
        
    return {"status": "ok", "synced_count": saved_count}

# To run locally: uvicorn main:app --reload
