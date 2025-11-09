from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from tensorflow.keras.models import load_model
import numpy as np
import cv2
import tempfile
import os

app = FastAPI(title="Suspicious Activity Detection API", version="1.0")

# Allow frontend or API client access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load your trained model
MODEL_PATH = "abnormalevent.h5"
model = load_model(MODEL_PATH)
print("✅ Model loaded successfully!")

@app.get("/")
def home():
    return {"message": "Suspicious Activity Detection API is running"}

@app.post("/predict/")
async def predict_video(file: UploadFile = File(...)):
    try:
        # Save uploaded file temporarily
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        temp.write(await file.read())
        temp.close()

        cap = cv2.VideoCapture(temp.name)
        if not cap.isOpened():
            return JSONResponse(content={"error": "Unable to read video"}, status_code=400)

        suspicious_count = 0
        total_frames = 0

        # Process all frames
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Preprocess frame
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, (64, 64))
            gray = gray.reshape(1, 64, 64, 1).astype("float32") / 255.0

            # Prediction
            pred = model.predict(gray, verbose=0)[0][0]
            label = 1 if pred > 0.5 else 0
            suspicious_count += label
            total_frames += 1

        cap.release()
        os.unlink(temp.name)

        # Calculate results
        suspicious_ratio = suspicious_count / total_frames if total_frames > 0 else 0
        result = "Suspicious Activity" if suspicious_ratio > 0.3 else "Normal Activity"

        return {
            "result": result,
            "suspicious_frames": suspicious_count,
            "total_frames": total_frames,
            "confidence": round(suspicious_ratio * 100, 2)
        }

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
