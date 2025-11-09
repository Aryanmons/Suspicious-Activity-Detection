import os
import cv2
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from tqdm import tqdm

# Suppress TensorFlow logging clutter
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# ================================
# CONFIG
# ================================
IMG_SIZE = (64, 64)
DATA_DIR = "data"
EPOCHS = 10
BATCH_SIZE = 8

print("🔹 Loading video frames...")

def load_one_frame_per_video(folder):
    frames = []
    for filename in tqdm(os.listdir(folder), desc=f"Loading from {folder}"):
        if filename.endswith(".mp4") or filename.endswith(".avi"):
            path = os.path.join(folder, filename)
            cap = cv2.VideoCapture(path)
            ret, frame = cap.read()
            cap.release()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frame = cv2.resize(frame, IMG_SIZE)
                frames.append(frame)
    return np.array(frames)

# ================================
# LOAD DATA
# ================================
abnormal_dir = os.path.join(DATA_DIR, "abnormal")
normal_dir = os.path.join(DATA_DIR, "normal")

abnormal = load_one_frame_per_video(abnormal_dir)
normal = load_one_frame_per_video(normal_dir)

X = np.concatenate((abnormal, normal), axis=0)
y = np.array([1]*len(abnormal) + [0]*len(normal))

X = X.reshape(-1, IMG_SIZE[0], IMG_SIZE[1], 1).astype("float32") / 255.0

print(f"✅ Loaded {len(X)} samples ({len(abnormal)} abnormal, {len(normal)} normal)")

# ================================
# SPLIT DATA
# ================================
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# ================================
# CNN MODEL
# ================================
model = models.Sequential([
    layers.Input(shape=(IMG_SIZE[0], IMG_SIZE[1], 1)),
    layers.Conv2D(32, (3, 3), activation='relu'),
    layers.MaxPooling2D(2, 2),
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D(2, 2),
    layers.Flatten(),
    layers.Dense(64, activation='relu'),
    layers.Dropout(0.3),
    layers.Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

print("\n🔹 Training started...\n")

# ================================
# TRAIN
# ================================
history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    verbose=1
)

# ================================
# EVALUATE & SUMMARY
# ================================
train_loss, train_acc = model.evaluate(X_train, y_train, verbose=0)
val_loss, val_acc = model.evaluate(X_val, y_val, verbose=0)

print(f"\n✅ Model saved as both abnormalevent.h5 and abnormalevent.keras")
model.save("abnormalevent.h5")
model.save("abnormalevent.keras")

print("\n📊 Training Summary:")
print(f"• Final Training Accuracy: {train_acc*100:.2f}%")
print(f"• Final Validation Accuracy: {val_acc*100:.2f}%")
print(f"• Final Training Loss: {train_loss:.4f}")
print(f"• Final Validation Loss: {val_loss:.4f}")

# ================================
# FIND BEST EPOCHS
# ================================
best_val_acc_epoch = np.argmax(history.history['val_accuracy']) + 1
best_val_loss_epoch = np.argmin(history.history['val_loss']) + 1
print(f"\n🏆 Best Validation Accuracy at Epoch {best_val_acc_epoch}: {max(history.history['val_accuracy'])*100:.2f}%")
print(f"💡 Lowest Validation Loss at Epoch {best_val_loss_epoch}: {min(history.history['val_loss']):.4f}")

# ================================
# PLOT TRAINING CURVES
# ================================
plt.figure(figsize=(10,5))

# Accuracy plot
plt.subplot(1,2,1)
plt.plot(history.history['accuracy'], label='Train Accuracy', marker='o')
plt.plot(history.history['val_accuracy'], label='Val Accuracy', marker='o')
plt.title('Model Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()
plt.grid(True)

# Loss plot
plt.subplot(1,2,2)
plt.plot(history.history['loss'], label='Train Loss', marker='o')
plt.plot(history.history['val_loss'], label='Val Loss', marker='o')
plt.title('Model Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig("training_metrics.png")
plt.show()

print("\n✅ Training Complete | All metrics saved to training_metrics.png")
