import cv2
import os
import numpy as np

# Create a dedicated directory for trained models
if not os.path.exists("models"):
    os.makedirs("models")

def train_identity(u_id):
    """
    Captures 30 biometric samples and trains a unique LBPH model 
    for the specified user identity.
    """
    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Using LBPH (Local Binary Patterns Histograms) for localized feature extraction
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    
    count = 0
    samples = []
    ids = []

    print(f"\n[SYSTEM] Initializing Training Sequence for ID: {u_id}")
    print("[INFO] Please rotate your face slightly for better feature mapping...")

    while count < 30:
        ret, img = cap.read()
        if not ret: break
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            count += 1
            # Extracting the Region of Interest (ROI) - The Face
            face_img = gray[y:y+h, x:x+w]
            samples.append(face_img)
            ids.append(u_id)
            
            # Visual feedback for the user
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(img, f"Captured: {count}/30", (x, y-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            
            cv2.imshow("Biometric Training Engine", img)
            
        if cv2.waitKey(1) & 0xFF == ord('q'): 
            break

    # Training the Local Model
    if len(samples) > 0:
        print("[PROCESS] Analyzing facial textures and generating histogram...")
        recognizer.train(samples, np.array(ids))
        
        # Save the trained model to a dedicated models folder
        model_path = f"models/trainer_{u_id}.yml"
        recognizer.write(model_path)
        print(f"[SUCCESS] Biometric model committed to: {model_path}")
    else:
        print("[ERROR] No samples captured. Training aborted.")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Example execution: Training ID 101
    train_identity(101)