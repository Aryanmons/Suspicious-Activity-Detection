import tkinter as tk
from tkinter.filedialog import askopenfilename
from PIL import Image, ImageTk
import numpy as np
import cv2
import os
from keras.models import load_model
from mail import send_alert

root = tk.Tk()
root.state('zoomed')
root.title("Suspicious Activity Detection")

img = Image.open("back5.jpg")
w, h = root.winfo_screenwidth(), root.winfo_screenheight()
img = img.resize((w, h))
bg = ImageTk.PhotoImage(img)

bg_label = tk.Label(root, image=bg)
bg_label.place(x=0, y=0)

heading = tk.Label(root, text="Suspicious Activity Detection", font=("Times New Roman", 45, "bold"), bg="#192841", fg="white")
heading.place(x=240, y=0)

def show_FDD_video(video_path):
    if not os.path.exists("abnormalevent.h5"):
        print("❌ Model file missing. Train first using Train_FDD_cnn.py.")
        return
    model = load_model("abnormalevent.h5")
    cap = cv2.VideoCapture(video_path)
    font = cv2.FONT_HERSHEY_SIMPLEX
    red, green = (0, 0, 255), (0, 255, 0)
    while True:
        ret, frame = cap.read()
        if not ret: break
        frame_resized = cv2.resize(frame, (64, 64))
        gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)
        img_array = gray.reshape(-1, 64, 64, 1).astype("float32") / 255
        prediction = model.predict(img_array)[0]
        label = "Suspicious" if prediction[1] > prediction[0] else "Normal"
        color = red if label == "Suspicious" else green
        cv2.putText(frame, f"Status: {label}", (20, 40), font, 1, color, 2)
        cv2.imshow("Detection", frame)
        if label == "Suspicious":
            send_alert()
        if cv2.waitKey(25) & 0xFF == 27:
            break
    cap.release()
    cv2.destroyAllWindows()

def Video_Verify():
    video_path = askopenfilename(filetypes=[("Video Files", "*.mp4")])
    if video_path:
        show_FDD_video(video_path)

button_detect = tk.Button(root, command=Video_Verify, text="Start Detection", width=20, font=("Times New Roman", 25, "bold"), bg="cyan", fg="black")
button_detect.place(x=100, y=150)

button_exit = tk.Button(root, command=root.destroy, text="Exit", width=20, font=("Times New Roman", 25, "bold"), bg="red", fg="white")
button_exit.place(x=100, y=300)

root.mainloop()
