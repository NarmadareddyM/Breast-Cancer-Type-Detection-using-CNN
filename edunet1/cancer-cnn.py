# -*- coding: utf-8 -*-
"""Untitled6.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Fl9bVfdPbsdGRD_liFaZldlrNluEW9HM
"""

# Install necessary libraries

import os
import subprocess
from pyngrok import ngrok

# Authenticate ngrok (Replace with your actual token)
subprocess.run(["ngrok", "authtoken", "2tdAfI41DQw3o0rkbqdL9E5QqIU_2WervUYcnFLtREyrQY1J"], check=True)

# Start Streamlit in the background
os.system("streamlit run app.py &")
# Install required libraries
subprocess.run(["pip", "install", "streamlit", "pyngrok", "opencv-python-headless", "numpy", "tensorflow", "scikit-learn", "zipfile36"], check=True)
subprocess.run(["pip", "install", "--user", "streamlit", "pyngrok", "opencv-python-headless", "numpy", "tensorflow", "scikit-learn", "zipfile36"], check=True)
import streamlit as st
import cv2
import numpy as np
import os
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
import zipfile
from pyngrok import ngrok
from google.colab import drive
drive.mount('/content/drive')
# Install necessary libraries
zip_path = "/content/drive/MyDrive/dataset.zip"  # Change this if the file is in a different folder
extract_path = "/content/dataset/"
import zipfile
import os

if os.path.exists(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    print("✅ Dataset extracted successfully.")
else:
    print("❌ Error: dataset.zip not found. Upload it to Google Drive or Colab.")



# 🔹 2️⃣ Load Images
def load_images_from_folder(folder, label):
    images, labels = [], []
    for filename in os.listdir(folder):
        img = cv2.imread(os.path.join(folder, filename), cv2.IMREAD_GRAYSCALE)
        if img is not None:
            img = cv2.resize(img, (64, 64))
            images.append(img)
            if 'benign' in filename:
                labels.append(1)
            elif 'malignant' in filename:
                labels.append(2)
            else:
                labels.append(0)
    return np.array(images), np.array(labels)

benign_images, benign_labels = load_images_from_folder(extract_path + "benign", 1)
malignant_images, malignant_labels = load_images_from_folder(extract_path + "malignant", 2)
normal_images, normal_labels = load_images_from_folder(extract_path + "normal", 0)

# 🔹 3️⃣ Preprocessing Data
X = np.concatenate((benign_images, malignant_images, normal_images), axis=0)
y = np.concatenate((benign_labels, malignant_labels, normal_labels), axis=0)
X = X / 255.0  # Normalize
X = X.reshape(-1, 64, 64, 1)  # Reshape for CNN
y = to_categorical(y, num_classes=3)  # One-hot encoding

# 🔹 4️⃣ Split dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 🔹 5️⃣ Define CNN model
model = Sequential([
    Conv2D(32, (3,3), activation='relu', input_shape=(64, 64, 1)),
    MaxPooling2D((2,2)),
    Conv2D(64, (3,3), activation='relu'),
    MaxPooling2D((2,2)),
    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.5),
    Dense(3, activation='softmax')
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# 🔹 6️⃣ Train model
model.fit(X_train, y_train, epochs=5, validation_data=(X_test, y_test))  # Reduced to 5 epochs for faster training

# 🔹 7️⃣ Function for Prediction
def predict_image(img, model):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.resize(img, (64, 64)) / 255.0
    img = img.reshape(1, 64, 64, 1)
    prediction = np.argmax(model.predict(img))

    if prediction == 1:
        return "Benign", "Non-cancerous tumor.", "Regular checkups recommended.", "#FFD700", "#ADD8E6", "#DDA0DD"
    elif prediction == 2:
        return "Malignant", "Cancerous tumor.", "Consult an oncologist.", "#FF4500", "#FFA07A", "#FF69B4"
    else:
        return "No Cancer", "No signs of cancer detected.", "Continue screening.", "#32CD32", "#20B2AA", "#9370DB"

# 🔹 8️⃣ Save model for Streamlit
model.save("/content/breast_cancer_model.h5")

# 🔹 9️⃣ Streamlit UI
app_code = """
import streamlit as st
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model

st.set_page_config(page_title="Breast Cancer Detection", layout="centered")
st.markdown("<h1 style='text-align: center; color: white; background-color: #0073e6; padding: 10px; border-radius: 10px;'>🔬 Breast Cancer Detection using CNN</h1>", unsafe_allow_html=True)

st.write("### Upload an image to classify it as:")
st.markdown("<h3 style='text-align: center; color: #FFD700;'>🟡 Benign</h3>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #FF4500;'>🔴 Malignant</h3>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #32CD32;'>🟢 Normal</h3>", unsafe_allow_html=True)

model = load_model("/content/breast_cancer_model.h5")

def predict_image(img, model):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.resize(img, (64, 64)) / 255.0
    img = img.reshape(1, 64, 64, 1)
    prediction = np.argmax(model.predict(img))

    if prediction == 1:
        return "Benign", "Non-cancerous tumor.", "Regular checkups recommended.", "#FFD700", "#ADD8E6", "#DDA0DD"
    elif prediction == 2:
        return "Malignant", "Cancerous tumor.", "Consult an oncologist.", "#FF4500", "#FFA07A", "#FF69B4"
    else:
        return "No Cancer", "No signs of cancer detected.", "Continue screening.", "#32CD32", "#20B2AA", "#9370DB"

uploaded_file = st.file_uploader("Choose an image...", type=["png", "jpg", "jpeg"])
if uploaded_file is not None:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    st.image(img, caption='📷 Uploaded Image', use_column_width=True, channels="BGR")

    if st.button("🔍 Predict Cancer Type"):
        cancer_type, description, suggestion, title_color, desc_color, sugg_color = predict_image(img, model)
        st.markdown(f"<h2 style='color: {title_color}; text-align: center;'>🏥 Prediction: {cancer_type}</h2>", unsafe_allow_html=True)
        st.markdown(f"<div style='background-color: {desc_color}; padding: 8px; border-radius: 8px;'><p style='color: white; font-size: 15px;'>📌 <b>Description:</b> {description}</p></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='background-color: {sugg_color}; padding: 8px; border-radius: 8px;'><p style='color: white; font-size: 15px;'>💡 <b>Suggestion:</b> {suggestion}</p></div>", unsafe_allow_html=True)
"""
import subprocess

# Install required libraries
subprocess.run(["pip", "install", "streamlit", "pyngrok", "opencv-python-headless", "numpy", "tensorflow", "scikit-learn", "zipfile36"], check=True)
subprocess.run(["pip", "install", "--user", "streamlit", "pyngrok", "opencv-python-headless", "numpy", "tensorflow", "scikit-learn", "zipfile36"], check=True)


import os
import subprocess
from pyngrok import ngrok

# Authenticate ngrok (Replace with your actual token)
subprocess.run(["ngrok", "authtoken", "2tdAfI41DQw3o0rkbqdL9E5QqIU_2WervUYcnFLtREyrQY1J"], check=True)

# Start Streamlit in the background
os.system("streamlit run app.py &")

# Connect ngrok to the Streamlit app (port 8501)
public_url = ngrok.connect(8501)
print(f"🔗 Public URL: {public_url}")

with open("app.py", "w") as f:
    f.write(app_code)

# 🔹 10️⃣ Set up ngrokimport subprocess

# Authenticate ngrok (Make sure the token is inside quotes!)
subprocess.run(["ngrok", "authtoken", "2tdAfI41DQw3o0rkbqdL9E5QqIU_2WervUYcnFLtREyrQY1J"], check=True)
  # Replace with your ngrok token
public_url = ngrok.connect("http://localhost:8501")
print(f"🔗 Public URL: {public_url}")

