import cv2
import time
import winsound
import subprocess
import threading
import numpy as np

# Global flags to synchronize audio alerts with live movement pace
is_audio_playing = False
last_alert_time = 0

def play_system_voice():
    """Uses native Windows PowerShell to announce alerts cleanly in the background."""
    global is_audio_playing
    is_audio_playing = True
    try:
        # 1. Console alert tone (Dual high-pitched beeps)
        winsound.Beep(2500, 200)
        winsound.Beep(2500, 200)
        
        # 2. Native Windows Speech command (Fast, robotic execution)
        phrase = "Attention. Attention. Irregularities detected in monitored zone."
        ps_command = f'Add-Type -AssemblyName System.Speech; $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synth.Rate = 1; $synth.Speak("{phrase}")'
        
        # Run hidden in background so it doesn't interrupt the camera feed
        subprocess.run(["powershell", "-Command", ps_command], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass
    is_audio_playing = False

def launch_industrial_cctv():
    global last_alert_time, is_audio_playing
    
    # Connect to DroidCam stream (Try 0, 1, or 2)
    cap = cv2.VideoCapture(1q) 
    
    if not cap.isOpened():
        print("❌ Error: Could not connect to DroidCam stream.")
        return

    # Advanced background subtractor matrix
    back_sub = cv2.createBackgroundSubtractorMOG2(history=300, varThreshold=60, detectShadows=False)

    print("\n🛡️ CCTV Industrial Edge Active: All Consoles Restored & Audio Synced!")
    print("Press 'q' inside either video window to shut down.")

    movement_start_time = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Calculate camera blockage (Anti-Tamper)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        average_brightness = np.mean(gray)

        # Process movement physics
        blurred_frame = cv2.GaussianBlur(frame, (5, 5), 0)
        fg_mask = back_sub.apply(blurred_frame)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        motion_detected = False

        for contour in contours:
            if cv2.contourArea(contour) < 3500: 
                continue
            
            motion_detected = True
            x, y, w, h = cv2.boundingRect(contour)
            # Draw an industrial red target box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # 🚨 THREAT EVALUATION MATRIX
        current_time = time.time()
        
        # Scenario 1: Camera covered or blocked
        if average_brightness < 12.0:
            status_color = (0, 0, 255)
            status_text = "⚠️ CRITICAL ANOMALY: CAMERA BLOCKED / TAMPERED"
            
            if not is_audio_playing and (current_time - last_alert_time > 4.0):
                last_alert_time = current_time
                threading.Thread(target=play_system_voice, daemon=True).start()

        # Scenario 2: Active movement detected
        elif motion_detected:
            if movement_start_time is None:
                movement_start_time = current_time
            
            duration = current_time - movement_start_time
            
            if duration > 1.5:  # Rapid response window
                status_color = (0, 0, 255)
                status_text = f"⚠️ BREACH: IRREGULAR MOVEMENT DETECTED ({int(duration)}s)"
                
                if not is_audio_playing and (current_time - last_alert_time > 4.5):
                    last_alert_time = current_time
                    threading.Thread(target=play_system_voice, daemon=True).start()
            else:
                status_color = (0, 165, 255)
                status_text = "SCANNING MOVEMENT PATTERN..."
        
        # Scenario 3: Secure
        else:
            movement_start_time = None
            status_color = (0, 255, 0)
            status_text = "🛡️ SYSTEM STATUS: SECURE"

        # UI Overlay Banner
        cv2.rectangle(frame, (0, 0), (frame.shape[1], 50), (10, 10, 10), -1)
        cv2.putText(frame, status_text, (20, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
        
        # 🖥️ DISPLAY BOTH CONSOLES
        cv2.imshow("Console 1: Live Warehouse Feed", frame)
        cv2.imshow("Console 2: Edge AI Vision Mask (What the CPU Sees)", fg_mask)

        # Listen for shutdown key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("🔒 System offline.")

if __name__ == "__main__":
    launch_industrial_cctv()