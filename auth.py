import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import logging

log = logging.getLogger("uvicorn")

security = HTTPBearer()

# Initialize Firebase Admin
def init_firebase():
    if not firebase_admin._apps:
        cred_path = os.getenv("FIREBASE_CREDENTIALS", "firebase-adminsdk.json")
        try:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            log.info("Firebase Admin initialized successfully.")
        except Exception as e:
            log.error(f"Failed to initialize Firebase Admin: {str(e)}")

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """
    Verifies the Firebase ID token and returns the user's UID.
    """
    token = credentials.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        return uid
    except Exception as e:
        log.warning(f"Invalid authentication token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
