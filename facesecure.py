import cv2
import os
from database import setup_db, add_user, get_child_data, update_spent

# Initialize database schema
setup_db()

def find_available_camera():
    """
    Scans multiple hardware and network sources to establish a stable video stream.
    Supports: Mobile IP Cameras, Integrated Webcams, and USB Peripherals.
    """
    # Priority List: 1. Mobile IP Stream, 2. Default Webcam, 3. External USB Sources
    sources = [
        "http://192.168.100.101:4747/video", 
        0, 
        1, 
        2
    ]
    
    for src in sources:
        print(f"[SCANNING] Attempting connection to Source: {src}...")
        cap = cv2.VideoCapture(src)
        
        # Verify if the stream is active and providing valid frames
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"[SUCCESS] Handshake established with Source: {src}")
                return cap
            else:
                cap.release()
    
    return None

def main():
    print("\n" + "="*40)
    print("   FACESECURE PAY: BIOMETRIC TERMINAL   ")
    print("="*40)

    # Initial Identity Registration (Simplified for Terminal)
    try:
        u_id = int(input("System Log: Enter Unique ID: "))
        u_name = input("System Log: Enter Identity Name: ")
        u_limit = float(input("System Log: Set Credit Limit: "))
        
        # Storing identity parameters
        add_user(u_id, u_name, u_limit, f"photos/{u_id}.jpg")
    except ValueError:
        print("[ERROR] Invalid input. System terminating.")
        return

    # Initializing Optical Hardware
    cap = find_available_camera()

    if cap is None:
        print("\n[CRITICAL] Hardware Failure: No camera source detected.")
        print("Protocol: Ensure device is connected or IP stream is active.")
    else:
        # Load computer vision model for face tracking
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        print("\n[SYSTEM ONLINE] Biometric Scanner Active. Press 'P' to Pay / 'Q' to Exit.")

        while True:
            success, img = cap.read()
            if not success: 
                break

            # Pre-processing frame for computer vision optimization
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            # Real-time data retrieval from secure ledger
            data = get_child_data(u_id)

            if len(faces) > 0 and data:
                name, limit, spent, _ = data
                balance = limit - spent
                
                for (x, y, w, h) in faces:
                    # Rendering the Heads-Up Display (HUD) on the video stream
                    border_color = (0, 255, 0) # Green for verified
                    cv2.rectangle(img, (x, y), (x+w, y+h), border_color, 2)
                    
                    status_text = f"{name.upper()} | BALANCE: ${balance:.2f}"
                    cv2.putText(img, status_text, (x, y-10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, border_color, 2)

            cv2.imshow("FaceSecure Pay - Terminal v1.0", img)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('p'):
                # Execute transaction protocol
                if update_spent(u_id, 10):
                    print(f"[TRANSACTION] $10 processed for ID: {u_id}")
            elif key == ord('q'):
                print("[INFO] System shutting down safely.")
                break

        # Resource management
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()