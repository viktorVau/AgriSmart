import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import os

# Paths
DATA_PATH = 'data/Crop_recommendation.csv'
MODEL_PATH = 'core/ml_models/crop_recommendation_model.pkl'
ENCODER_PATH = 'core/ml_models/label_encoder.pkl'

# Create ml_models dir if not exists
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

# Load dataset
df = pd.read_csv(DATA_PATH)

# Features and target
X = df.drop('label', axis=1)
y = df['label']

# Encode labels
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save model and encoder
joblib.dump(model, MODEL_PATH)
joblib.dump(label_encoder, ENCODER_PATH)

print("✅ Model and encoder saved successfully.")
