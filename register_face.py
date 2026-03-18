import cv2
import os

# --- 1. SETUP ---
if not os.path.exists("photos"):
    os.makedirs("photos")

cap = cv2.VideoCapture(0)

print("--- FaceSecure Enrollment System ---")
user_id = input("Enter Student ID for Registration (e.g. 101): ")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Display Instructions
    cv2.putText(frame, f"Registering ID: {user_id}", (30, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.putText(frame, "Center your face & Press 'S' to Save", (30, 90), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
    cv2.putText(frame, "Press 'Q' to Cancel", (30, 130), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)

    # Face Frame Guide (Aik box taake user sahi position mein khara ho)
    cv2.rectangle(frame, (200, 120), (440, 360), (30, 126, 191), 2)

    cv2.imshow("Enrollment - FaceSecure Pay", frame)

    key = cv2.waitKey(1) & 0xFF

    # Save logic
    if key == ord('s'):
        # Sirf ID ke naam se save karein taake recognition script ko confusion na ho
        img_name = f"photos/{user_id}.jpg"
        cv2.imwrite(img_name, frame)
        print(f"[SUCCESS] Face for User {user_id} saved at {img_name}")
        break

    elif key == ord('q'):
        print("[CANCELLED] Registration stopped.")
        break

cap.release()
cv2.destroyAllWindows()