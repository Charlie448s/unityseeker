import cv2
import mediapipe as mp
import ctypes
import os
import winreg

# Function to get the current Windows wallpaper
def get_current_wallpaper():
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 "Control Panel\\Desktop", 0, winreg.KEY_READ)
        wallpaper_path, _ = winreg.QueryValueEx(reg_key, "WallPaper")
        return wallpaper_path
    except Exception as e:
        print("[ERROR] Unable to get current wallpaper:", e)
        return ""

# Function to change wallpaper (Windows only)
def set_wallpaper(image_path):
    SPI_SETDESKWALLPAPER = 20
    # 3 = update the user profile + send change broadcast
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, image_path, 3)

# === MediaPipe Setup ===
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

def detect_hand_and_toggle_wallpaper():
    # Get current wallpaper as default
    default_wallpaper = get_current_wallpaper()
    if not os.path.exists(default_wallpaper):
        print(f"[ERROR] Wallpaper not found: {default_wallpaper}")
        return

    # Set your hand-up wallpaper here
    hand_up_wallpaper = os.path.abspath("D:/Downloads/adolf-anarchy-dark-evil-wallpaper-preview.jpg")
    if not os.path.exists(hand_up_wallpaper):
        print(f"[ERROR] Please place a file named 'hand_up.jpg' in this folder.")
        return

    cap = cv2.VideoCapture(0)
    hand_is_up = False

    print("[INFO] Raise your hand to change wallpaper.")
    print("[INFO] Press ESC to exit.")

    while True:
        success, img = cap.read()
        if not success:
            print("[ERROR] Failed to read webcam.")
            break

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)
            if not hand_is_up:
                print("[INFO] Hand detected — setting new wallpaper.")
                set_wallpaper(hand_up_wallpaper)
                hand_is_up = True
            cv2.putText(img, "Hand Detected", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            if hand_is_up:
                print("[INFO] Hand gone — reverting wallpaper.")
                set_wallpaper(default_wallpaper)
                hand_is_up = False
            cv2.putText(img, "No Hand", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow("Camera Feed", img)

        if cv2.waitKey(10) == 27:
            print("[INFO] Exiting.")
            break

    cap.release()
    cv2.destroyAllWindows()
    # Ensure wallpaper is restored on exit
    if hand_is_up:
        set_wallpaper(default_wallpaper)

if __name__ == "__main__":
    detect_hand_and_toggle_wallpaper()
