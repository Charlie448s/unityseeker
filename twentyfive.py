import os
import sys
import queue
import json
import time
import subprocess
import sounddevice as sd
import pyautogui
from vosk import Model, KaldiRecognizer
#vosku voskov
# Paths
MODEL_PATH = "vosk-model-small-en-us-0.15"

# Load Vosk model
if not os.path.exists(MODEL_PATH):
    print("Download and unzip a Vosk model into the current folder.")
    sys.exit()

model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, 16000)
q = queue.Queue()

# Audio callback
def callback(indata, frames, time_info, status):
    if status:
        print(status)
    q.put(bytes(indata))

# Open or focus VS Code
def open_or_focus_vscode():
    try:
        subprocess.Popen(["code"])
        print("Opening VS Code...")
        time.sleep(5)  # wait for VS Code to load
    except Exception as e:
        print("Failed to open VS Code:", e)

# Open terminal and set Git Bash
def switch_to_git_bash():
    print("Switching terminal to Git Bash...")

    # Open terminal (Ctrl + `)
    pyautogui.hotkey("ctrl", "`")
    time.sleep(1)

    # Open command palette (Ctrl + Shift + P)
    pyautogui.hotkey("ctrl", "shift", "p")
    time.sleep(1)

    # Type "Select Default Profile"
    pyautogui.typewrite("Select Default Profile")
    time.sleep(1)
    pyautogui.press("enter")
    time.sleep(1)

    # Select Git Bash from the list
    pyautogui.typewrite("Git Bash")
    pyautogui.press("enter")
    time.sleep(1)

    # Open new terminal (Ctrl + Shift + `)
    pyautogui.hotkey("ctrl", "shift", "`")
    print("Git Bash terminal opened.")

# Voice-based command loop
def listen_and_navigate():
    print("🎤 Listening... Say 'open VS Code', 'switch to Git Bash', or 'exit'")

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                text = json.loads(result)["text"]
                print(f"You said: {text}")

                if "open vs code" in text:
                    open_or_focus_vscode()

                elif "switch to git bash" in text or "open git bash" in text:
                    switch_to_git_bash()

                elif "exit" in text or "quit" in text:
                    print("Exiting.")
                    break

# Run
if __name__ == "__main__":
    listen_and_navigate()
