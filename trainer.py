import cv2
import os
import numpy as np

def train_face(u_id):
    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    
    count = 0
    print(f"[INFO] Training for ID: {u_id}. Look at the camera...")
    
    samples = []
    ids = []

    while count < 30: # 30 photos kafi hain
        ret, img = cap.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            count += 1
            face_img = gray[y:y+h, x:x+w]
            samples.append(face_img)
            ids.append(u_id)
            cv2.imshow("Training...", img)
            
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    # Training the model
    recognizer.train(samples, np.array(ids))
    recognizer.write(f"trainer_{u_id}.yml")
    print(f"[SUCCESS] Face learned for ID {u_id}!")
    cap.release()
    cv2.destroyAllWindows()