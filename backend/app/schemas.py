from pydantic import BaseModel

from typing import Literal 

class PredictionRequest(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

class PredictionResponse(BaseModel):
    prediction: int

class JobSubmissionResponse(BaseModel):
    job_id:str
    status: Literal["queued"]

class JobStatusResponse(BaseModel):
    job_id: str
    status: Literal[
        "queued",
        "processing",
        "completed",
        "failed"
    ]

    prediction: int | None = None
    error: str | None = None


class WorkerInfo(BaseModel):
    worker_id: str
    status: Literal["alive"]
    last_heartbeat: float

class WorkerResponse(BaseModel):
    count: int
    workers: list[WorkerInfo]