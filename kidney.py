import cv2
import mediapipe as mp
import time
import os
import subprocess
#hola migos

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

# Track hand X positions
wave_positions = []
wave_time_window = 1.5  # seconds

cap = cv2.VideoCapture(0)
start_time = time.time()

def detect_wave(wave_positions):
    if len(wave_positions) < 5:
        return False

    x_positions = [pos[0] for pos in wave_positions]
    min_x = min(x_positions)
    max_x = max(x_positions)

    if (max_x - min_x) > 0.2:
        return True
    return False

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    current_time = time.time()

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get X coordinate of wrist
            wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
            wave_positions.append((wrist.x, current_time))

            # Keep only recent positions within time window
            wave_positions = [(x, t) for x, t in wave_positions if current_time - t < wave_time_window]

            if detect_wave(wave_positions):
                print("👋 Wave detected! Closing VS Code...")
                cap.release()
                cv2.destroyAllWindows()
                
                # Kill VS Code gracefully on Windows
                try:
                    subprocess.run(["taskkill", "/F", "/IM", "Code.exe"], check=True)
                except subprocess.CalledProcessError:
                    print("Failed to close VS Code. Make sure it's running.")
                exit()

    cv2.putText(frame, "Wave to close VS Code", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("Wave Detector", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # Esc to exit manually
        break

cap.release()
cv2.destroyAllWindows()
