import tkinter as tk
from PIL import Image, ImageTk
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tkinter import filedialog, messagebox
import time
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# ================================
# EMAIL SETTINGS
# ================================
SENDER_EMAIL = "aryan1707golu@gmail.com"        # your email
SENDER_PASSWORD = "aaeo tedj izcc vfrn"        # app password (not normal password)
RECEIVER_EMAIL = "aryan1707br@gmail.com" # recipient’s email

# ================================
# EMAIL FUNCTION
# ================================
def send_email_alert(video_name, suspicious_frames, total_frames, confidence):
    subject = "🚨 Suspicious Activity Detected"
    body = f"""
    Suspicious activity detected during video analysis.

    📁 Video: {video_name}
    ⚠️ Suspicious Frames: {suspicious_frames} / {total_frames}
    📊 Confidence: {confidence:.2f}%
    🕒 Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

    Please review the CCTV footage immediately.
    """

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("📩 Email alert sent successfully!")
    except Exception as e:
        print("❌ Failed to send email:", e)

# ================================
# LOAD MODEL
# ================================
MODEL_PATH = "abnormalevent.h5"
if not os.path.exists(MODEL_PATH):
    messagebox.showerror("Error", "Model file not found! Train the model first.")
    exit()

model = load_model(MODEL_PATH)
print("✅ Model Loaded Successfully")

# ================================
# SETUP MAIN WINDOW
# ================================
root = tk.Tk()
root.title("Suspicious Activity Detection")
root.state('zoomed')
root.configure(bg="#1a1a1a")

screen_w, screen_h = root.winfo_screenwidth(), root.winfo_screenheight()

# ================================
# BACKGROUND DESIGN
# ================================
bg_canvas = tk.Canvas(root, width=screen_w, height=screen_h, bg="#1a1a1a", highlightthickness=0)
bg_canvas.pack(fill="both", expand=True)

title_text = bg_canvas.create_text(
    screen_w / 2, 50,
    text="🔍 Suspicious Activity Detection System",
    fill="cyan",
    font=("Segoe UI", 36, "bold")
)

# ================================
# VIDEO DISPLAY AREA
# ================================
video_label = tk.Label(root, bg="#1a1a1a")
video_label.place(relx=0.5, rely=0.55, anchor=tk.CENTER)

status_label = tk.Label(
    root, text="Load a video to start detection",
    font=("Segoe UI", 18, "italic"), bg="#1a1a1a", fg="white"
)
status_label.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

# ================================
# FUNCTION: RUN DETECTION
# ================================
def detect_suspicious_activity(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        messagebox.showerror("Error", "Unable to open video.")
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    suspicious_count = 0
    frame_width, frame_height = 640, 480

    status_label.config(text="Detection Running...", fg="yellow")
    print("🎥 Detection started...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break  # end of video

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, (64, 64))
        gray = gray.reshape(1, 64, 64, 1).astype("float32") / 255.0

        pred = model.predict(gray, verbose=0)
        label = "Suspicious Activity" if pred[0][0] > 0.5 else "Normal Activity"
        color = (0, 0, 255) if label == "Suspicious Activity" else (0, 255, 0)

        if label == "Suspicious Activity":
            suspicious_count += 1

        cv2.putText(frame, label, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
        cv2.rectangle(frame, (10, 10), (frame.shape[1]-10, frame.shape[0]-10), color, 2)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb_frame)
        imgtk = ImageTk.PhotoImage(image=img.resize((frame_width, frame_height)))

        video_label.config(image=imgtk)
        video_label.image = imgtk
        root.update_idletasks()
        root.update()

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()

    suspicious_ratio = suspicious_count / total_frames * 100 if total_frames > 0 else 0
    result_text = (
        f"Suspicious Frames: {suspicious_count}/{total_frames} | "
        f"Confidence: {suspicious_ratio:.2f}%"
    )

    if suspicious_ratio > 30:
        status_label.config(text="🚨 Suspicious Activity Detected! Email Sent!", fg="red")
        send_email_alert(os.path.basename(video_path), suspicious_count, total_frames, suspicious_ratio)
    else:
        status_label.config(text="✅ Normal Activity", fg="lime")

    print("✅ Detection complete")

# ================================
# FUNCTION: LOAD VIDEO
# ================================
def load_video():
    file_path = filedialog.askopenfilename(
        title="Select a Video",
        filetypes=[("Video Files", "*.mp4 *.avi *.mov")]
    )
    if file_path:
        status_label.config(text="Video Loaded: " + os.path.basename(file_path), fg="white")
        root.after(1000, lambda: detect_suspicious_activity(file_path))

# ================================
# BUTTONS
# ================================
btn_style = {"font": ("Segoe UI", 18, "bold"), "width": 18, "height": 1, "bg": "#00b4d8", "fg": "white"}

load_btn = tk.Button(root, text="🎬 Select Video", command=load_video, **btn_style)
load_btn.place(relx=0.35, rely=0.15, anchor=tk.CENTER)

exit_btn = tk.Button(root, text="❌ Exit", command=root.destroy, **btn_style)
exit_btn.place(relx=0.65, rely=0.15, anchor=tk.CENTER)

# ================================
# RUN LOOP
# ================================
root.mainloop()
