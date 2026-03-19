import cv2
from deepface import DeepFace
from database import update_spent, can_user_pay
import os
import numpy as np
import time

# --- HARDWARE INITIALIZATION ---
cap = cv2.VideoCapture(0)
camera_available = cap.isOpened()

if not camera_available:
    print("[SYSTEM WARNING] Camera hardware not detected. Entering Virtual Simulation Mode.")

print("[SYSTEM ONLINE] FaceSecure AI Terminal is Scanning for Identities...")

while True:
    if camera_available:
        ret, frame = cap.read()
        if not ret: break
    else:
        # Simulation Mode: Creates a digital standby screen if no camera is found
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(frame, "SIMULATION MODE: NO CAMERA", (120, 240), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        ret = True

    u_id = None
    # Creating a distinct display layer for HUD elements
    display_frame = frame.copy() 

    try:
        if camera_available:
            # --- AI BIOMETRIC RECOGNITION ---
            # Using VGG-Face model for high-accuracy identity verification
            results = DeepFace.find(img_path=frame, 
                                    db_path="photos", 
                                    enforce_detection=False, 
                                    model_name="VGG-Face",
                                    detector_backend="opencv", 
                                    silent=True)

            if len(results) > 0 and not results[0].empty:
                match = results[0].iloc[0]
                # Metric Threshold: Lower cosine distance means higher confidence
                if match['VGG-Face_cosine'] < 0.4: 
                    identity_path = match['identity'] 
                    u_id = os.path.basename(identity_path).split('.')[0]
                    
                    # --- SUCCESS UI HUD ---
                    # Futuristic bounding box for verified subjects
                    cv2.rectangle(display_frame, (180, 130), (460, 350), (0, 255, 0), 2)
                    cv2.putText(display_frame, f"VERIFIED ID: {u_id}", (50, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                    cv2.putText(display_frame, "COMMAND: Press 'P' to Authorize $10", (50, 90), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    except Exception:
        # Silently handle recognition timeouts or frame drops
        pass

    cv2.imshow("FaceSecure Pay - AI Terminal", display_frame)

    key = cv2.waitKey(1) & 0xFF
    
    # --- TRANSACTION PROTOCOL ---
    if key == ord('p') and u_id: 
        # Verify credit integrity from secure ledger
        allowed, msg = can_user_pay(int(u_id), 10)
        
        # Create a visual overlay for transaction feedback
        feedback_overlay = display_frame.copy()
        cv2.rectangle(feedback_overlay, (0,0), (640, 480), (0,0,0), -1)
        
        if allowed:
            # Commit transaction to database and blockchain
            update_spent(int(u_id), 10)
            
            # --- TRANSACTION SUCCESS SCREEN ---
            screen = cv2.addWeighted(feedback_overlay, 0.8, display_frame, 0.2, 0)
            cv2.putText(screen, "PAYMENT AUTHORIZED", (120, 240), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
            cv2.putText(screen, f"ID: {u_id} | DEBIT: $10.00", (180, 280), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        else:
            # --- TRANSACTION DECLINED SCREEN ---
            screen = cv2.addWeighted(feedback_overlay, 0.8, display_frame, 0.2, 0)
            cv2.putText(screen, "TRANSACTION DECLINED", (130, 220), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 0, 255), 3)
            cv2.putText(screen, f"REASON: {msg.upper()}", (160, 270), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)

        cv2.imshow("FaceSecure Pay - AI Terminal", screen)
        cv2.waitKey(2000) # Pause for 2 seconds to allow visual confirmation
        
    elif key == ord('q'):
        print("[INFO] Terminating AI engine and releasing hardware.")
        break

cap.release()
cv2.destroyAllWindows()