import cv2
from deepface import DeepFace
from database import update_spent, can_user_pay  # can_user_pay ko bhi import kar liya
os import os
import numpy as np

# --- 1. CAMERA SETUP ---
cap = cv2.VideoCapture(0)
camera_available = cap.isOpened()

if not camera_available:
    print(">> SYSTEM: Camera nahi mila! Testing mode active.")

print(">> SYSTEM LIVE: FaceSecure Terminal is Scanning...")

while True:
    if camera_available:
        ret, frame = cap.read()
        if not ret: break
    else:
        # PC Par camera nahi toh black screen dikhaye
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(frame, "NO CAMERA DETECTED", (150, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        ret = True

    u_id = None
    display_frame = frame.copy() # Display ke liye alag frame taake original clean rahe

    try:
        if camera_available:
            # Face ko dhundna
            results = DeepFace.find(img_path=frame, 
                                    db_path="photos", 
                                    enforce_detection=False, 
                                    model_name="VGG-Face",
                                    detector_backend="opencv", 
                                    silent=True)

            if len(results) > 0 and not results[0].empty:
                match = results[0].iloc[0]
                # Agar face match ho jaye (0.4 threshold)
                if match['VGG-Face_cosine'] < 0.4: 
                    identity = match['identity'] 
                    u_id = os.path.basename(identity).split('.')[0]
                    
                    # UI Elements - Green Box for detection
                    cv2.rectangle(display_frame, (180, 130), (460, 350), (0, 255, 0), 2)
                    cv2.putText(display_frame, f"Verified ID: {u_id}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(display_frame, "Press 'P' to Pay $10", (50, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    except Exception as e:
        pass

    cv2.imshow("FaceSecure Pay - Terminal", display_frame)

    key = cv2.waitKey(1) & 0xFF
    
    # --- PAYMENT LOGIC ---
    if key == ord('p') and u_id: 
        # 1. Database se check karein ke gunjaish hai ya nahi
        allowed, msg = can_user_pay(int(u_id), 10)
        
        # Overlay setup for feedback
        overlay = display_frame.copy()
        cv2.rectangle(overlay, (0,0), (640, 480), (0,0,0), -1)
        
        if allowed:
            # Payment Karo
            update_spent(int(u_id), 10)
            print(f"[SUCCESS] $10 deducted from User {u_id}")
            
            # Green Success Screen
            feedback_frame = cv2.addWeighted(overlay, 0.7, display_frame, 0.3, 0)
            cv2.putText(feedback_frame, "PAYMENT SUCCESSFUL", (120, 240), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
            cv2.putText(feedback_frame, f"ID: {u_id} | Amount: $10", (180, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        else:
            # Denied Logic
            print(f"[DENIED] {msg}")
            
            # Red Error Screen
            feedback_frame = cv2.addWeighted(overlay, 0.8, display_frame, 0.2, 0)
            cv2.putText(feedback_frame, "ACCESS DENIED", (170, 220), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
            cv2.putText(feedback_frame, "LIMIT EXCEEDED", (200, 270), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(feedback_frame, f"ID: {u_id}", (280, 310), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        cv2.imshow("FaceSecure Pay - Terminal", feedback_frame)
        cv2.waitKey(2000) # 2 seconds ka stay taake result nazar aaye
        
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()