# core/predict.py

import numpy as np
import joblib
import os
from django.conf import settings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'ml_models', 'crop_recommendation_model.pkl')
ENCODER_PATH = os.path.join(BASE_DIR, 'ml_models', 'label_encoder.pkl')

model = joblib.load(MODEL_PATH)
label_encoder = joblib.load(ENCODER_PATH)

def recommend_crop(data, top_n=3):
    input_array = np.array([[ 
        data['N'], data['P'], data['K'], 
        data['temperature'], data['humidity'], 
        data['ph'], data['rainfall']
    ]])
    
    probabilities = model.predict_proba(input_array)[0]
    top_indices = probabilities.argsort()[-top_n:][::-1]
    
    top_crops = label_encoder.inverse_transform(top_indices)
    top_probs = [round(probabilities[i] * 100, 2) for i in top_indices]
    
    return list(zip(top_crops, top_probs))  # Returns list of tuples: [(crop1, prob1), ...]


# def recommend_crop(data):
#     input_array = np.array([[
#         data['N'], data['P'], data['K'],
#         data['temperature'], data['humidity'],
#         data['ph'], data['rainfall']
#     ]])
#     prediction = model.predict(input_array)
#     crop_label = label_encoder.inverse_transform(prediction)[0]
#     return crop_label