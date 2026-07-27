from fastapi import FastAPI , HTTPException

from app.model_service import ModelService

from app.schemas import (PredictionRequest, 
                         PredictionResponse, 
                         JobSubmissionResponse, 
                         JobStatusResponse)

import json

from uuid import uuid4

from app.redis_client import (
    INFERENCE_QUEUE,
    get_job_key,
    redis_client
)

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

@app.post("/jobs/predict",
          response_model= JobSubmissionResponse)

def submit_prediction_job(
    request: PredictionRequest) -> JobSubmissionResponse:
    job_id= str(uuid4())

    features = [
        request.sepal_length,
        request.sepal_width,
        request.petal_length,
        request.petal_width,
    ]

    job= {
        "job_id": job_id,
        "features": features,
    }

    job_status={
        "job_id": job_id,
        "status": "queued",
        "prediction": None,
        "error": None
    }

    redis_client.set(
        get_job_key(job_id),
        json.dumps(job_status),
        ex= 3600
    )

    redis_client.lpush(
        INFERENCE_QUEUE,
        json.dumps(job)
    )

    return JobSubmissionResponse(
        job_id= job_id,
        status= "queued"
    )

@app.get(
    "/jobs/{job_id}",
    response_model=JobStatusResponse
)
def get_job_status(
    job_id: str
) -> JobStatusResponse:

    job_data = redis_client.get(
        get_job_key(job_id)
    )

    if job_data is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    job = json.loads(job_data)

    return JobStatusResponse(**job)