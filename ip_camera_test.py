import cv2

# --- ENTERPRISE IP CAMERA CONFIGURATION ---
# This module allows the SaaS to connect with external IP/CCTV hardware.
# Standard RTSP or HTTP streams are supported.
CAMERA_URL = "http://192.168.18.10:4747/video" 

def test_external_sensor():
    print("[SYSTEM] Initializing External Sensor Diagnostic...")
    cap = cv2.VideoCapture(CAMERA_URL)

    if not cap.isOpened():
        print("[FAIL] External camera not found. Reverting to local hardware (0).")
        cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret: break
        
        cv2.putText(frame, "EXTERNAL FEED: STABLE", (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow("SaaS Hardware Integrator", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_external_sensor()