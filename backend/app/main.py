from fastapi import FastAPI , HTTPException

from app.model_service import ModelService
from app.schemas import PredictionRequest, PredictionResponse

app= FastAPI(title= "Destributed AI Inference Cloud",
            version= "0.1.0")

model_service= ModelService()

@app.get("/")

def root():
    return {
        "message": "Distributed AI Inference Cloud API"
    }

@app.get("/health")

def health():
    return {
        "status": "healthy"
    }

@app.post(
    "/predict",
    response_model= PredictionResponse)

def predict(
    request: PredictionRequest) -> PredictionResponse:

    try:
        features= [
            request.sepal_length,
            request.sepal_width,
            request.petal_length,
            request.petal_width,

        ]

        prediction= model_service.predict(features)

        return PredictionResponse(
            prediction= prediction
        )


    except Exception as error:
    
        print("Prediction error:", error)

        raise HTTPException(
            status_code=500,
            detail="Inference failed"
        ) from error