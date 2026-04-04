import cv2
import os
import time
from fastapi import FastAPI
from deepface import DeepFace
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory to store registered user photos
USER_DB_PATH = "photos"
if not os.path.exists(USER_DB_PATH):
    os.makedirs(USER_DB_PATH)

@app.post("/register")
async def register_user(user_id: str):
    """
    Captures and saves a master photo for a new user.
    """
    cap = cv2.VideoCapture(0)
    time.sleep(1)
    ret, frame = cap.read()
    cap.release()

    if ret:
        # Save photo with user's ID as filename
        photo_path = os.path.join(USER_DB_PATH, f"{user_id}.jpg")
        cv2.imwrite(photo_path, frame)
        return {"status": "SUCCESS", "message": f"User {user_id} registered successfully."}
    
    return {"status": "ERROR", "message": "Failed to capture registration photo."}

@app.post("/verify")
async def verify_transaction(user_id: str):
    """
    Matches live face scan against the registered master photo.
    """
    # 1. Check if user exists in our records
    reference_path = os.path.join(USER_DB_PATH, f"{user_id}.jpg")
    if not os.path.exists(reference_path):
        return {"status": "FAILED", "message": "User not registered."}

    # 2. Capture live frame for verification
    cap = cv2.VideoCapture(0)
    time.sleep(1)
    ret, live_frame = cap.read()
    cap.release()

    if not ret:
        return {"status": "ERROR", "message": "Camera access denied."}

    temp_scan = "current_scan.jpg"
    cv2.imwrite(temp_scan, live_frame)

    try:
        # 3. AI Comparison: Live Scan vs. Registered Master Photo
        result = DeepFace.verify(
            img1_path = temp_scan, 
            img2_path = reference_path,
            model_name = 'VGG-Face'
        )

        if result["verified"]:
            return {"status": "SUCCESS", "message": "Identity Verified. Processing Transaction..."}
        else:
            return {"status": "FAILED", "message": "Face mismatch. Transaction Terminated."}

    except Exception as e:
        return {"status": "ERROR", "message": "Face detection failed. Try again."}