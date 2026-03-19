import cv2
import os

# --- SYSTEM INITIALIZATION ---
# Ensure the biometric repository exists
if not os.path.exists("photos"):
    os.makedirs("photos")

def start_enrollment():
    """
    Manages the manual capture of biometric face samples for new identity registration.
    """
    cap = cv2.VideoCapture(0)
    
    print("\n" + "="*40)
    print("   FACESECURE: BIOMETRIC ENROLLMENT   ")
    print("="*40)
    
    # Validation: Ensure User ID is provided before opening the shutter
    user_id = input("System Log: Enter Student ID for Enrollment: ").strip()
    
    if not user_id:
        print("[ERROR] Identity registration requires a valid ID. Termination.")
        return

    print(f"[INFO] Initializing sensor for ID: {user_id}")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[CRITICAL] Optical sensor failure.")
            break

        # --- HEADS-UP DISPLAY (HUD) ---
        # Displaying real-time enrollment status
        cv2.putText(frame, f"ENROLLING ID: {user_id}", (30, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.putText(frame, "ACTION: Press 'S' to Commit Identity", (30, 90), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        cv2.putText(frame, "ACTION: Press 'Q' to Abort", (30, 120), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)

        # Positioning Guide: Ensures face alignment within the optimal capture zone
        # Drawing a futuristic bounding box for the user
        cv2.rectangle(frame, (200, 120), (440, 380), (30, 126, 191), 2)
        cv2.putText(frame, "ALIGN FACE WITHIN BOUNDS", (200, 110), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (30, 126, 191), 1)

        cv2.imshow("Enrollment Terminal - FaceSecure Pay", frame)

        key = cv2.waitKey(1) & 0xFF

        # --- COMMIT LOGIC ---
        if key == ord('s'):
            # Saving image with standard naming convention for the recognition engine
            img_path = f"photos/{user_id}.jpg"
            cv2.imwrite(img_path, frame)
            
            # Flush existing AI representations to force a system re-index
            cache_file = "photos/representations_vgg_face.pkl"
            if os.path.exists(cache_file):
                os.remove(cache_file)
                print("[INFO] Biometric cache cleared for re-indexing.")
                
            print(f"[SUCCESS] Biometric signature for ID {user_id} committed to {img_path}")
            break

        # --- ABORT LOGIC ---
        elif key == ord('q'):
            print("[ABORTED] Registration sequence terminated by operator.")
            break

    # Release hardware resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    start_enrollment()