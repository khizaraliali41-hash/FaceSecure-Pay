import cv2
import os
import uvicorn
from fastapi import FastAPI, UploadFile, File, Form
from deepface import DeepFace
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI App
app = FastAPI(title="FaceSecure Pay - Biometric Transaction System")

# Configure CORS for Frontend Integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants & Configurations
USER_DB_PATH = "photos"
MODEL_NAME = "VGG-Face"

# Ensure storage directory exists
if not os.path.exists(USER_DB_PATH):
    os.makedirs(USER_DB_PATH)

@app.get("/")
async def root():
    """Health check endpoint to verify API status."""
    return {
        "status": "Online",
        "message": "FaceSecure Pay API is Running",
        "version": "1.0.0"
    }

@app.post("/register")
async def register_user(user_id: str = Form(...), file: UploadFile = File(...)):
    """
    Registers a new user by saving their master photo.
    Note: Photos are uploaded from frontend as Railway lacks hardware camera access.
    """
    try:
        photo_path = os.path.join(USER_DB_PATH, f"{user_id}.jpg")
        
        # Save uploaded file to local storage
        with open(photo_path, "wb") as buffer:
            buffer.write(await file.read())
        
        return {
            "status": "SUCCESS", 
            "message": f"User {user_id} registered successfully."
        }
    except Exception as e:
        return {"status": "ERROR", "message": f"Registration failed: {str(e)}"}

@app.post("/verify")
async def verify_transaction(user_id: str = Form(...), file: UploadFile = File(...)):
    """
    Authenticates a transaction by comparing live upload against registered photo.
    Uses DeepFace for AI-based facial verification.
    """
    reference_path = os.path.join(USER_DB_PATH, f"{user_id}.jpg")
    
    # Pre-verification checks
    if not os.path.exists(reference_path):
        return {"status": "FAILED", "message": "User not registered in the system."}

    # Temporarily save live scan for AI processing
    temp_scan = f"temp_{user_id}.jpg"
    with open(temp_scan, "wb") as buffer:
        buffer.write(await file.read())

    try:
        # DeepFace Verification Logic
        result = DeepFace.verify(
            img1_path = temp_scan, 
            img2_path = reference_path,
            model_name = MODEL_NAME,
            enforce_detection = False  # Prevents crash if face is partially obscured
        )

        # Cleanup temporary file
        if os.path.exists(temp_scan):
            os.remove(temp_scan)

        if result["verified"]:
            return {
                "status": "SUCCESS", 
                "message": "Identity Verified. Processing Transaction..."
            }
        
        return {
            "status": "FAILED", 
            "message": "Face mismatch. Transaction Terminated."
        }

    except Exception as e:
        return {"status": "ERROR", "message": "Facial processing engine error."}

# Entry point for Railway/Uvicorn
if __name__ == "__main__":
    # Dynamically assign port for Cloud Deployment
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)