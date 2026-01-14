# ai/main.py

from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import os

from ai.features import extract_features

app = FastAPI(title="AI Recommendation Service")

# Always resolve path correctly (this avoids 90% of bugs)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")

model = joblib.load(MODEL_PATH)


class RecommendRequest(BaseModel):
    orderbook: dict
    order: dict


@app.post("/ai/recommend")
def recommend(req: RecommendRequest):
    features = extract_features(req.orderbook, req.order)
    prob = model.predict_proba([features])[0][1]

    return {
        "fill_probability": round(float(prob), 3)
    }


@app.get("/health")
def health():
    return {"status": "ok"}
