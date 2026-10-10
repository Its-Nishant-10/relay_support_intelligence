from __future__ import annotations

from functools import lru_cache

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from relay.policy import apply_policy, load_policy
from relay.predictor import Predictor

app = FastAPI(title="Relay Support Intelligence API", version="2.0.0")


class TicketRequest(BaseModel):
    subject: str = ""
    description: str


@lru_cache(maxsize=1)
def get_predictor() -> Predictor:
    return Predictor()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/predict")
def predict(request: TicketRequest) -> dict:
    try:
        predictor = get_predictor()
        text = f"{request.subject} {request.description}".strip()
        prediction = predictor.predict_ticket(text)
        policy = apply_policy(text, prediction, load_policy())
        return {
            "ml_prediction": prediction.to_dict(),
            "final_decision": policy.to_dict(),
        }
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
