import json
import threading 
import time 

from app.model_service import ModelService

from app.redis_client import (INFERENCE_QUEUE,
                              get_job_key, 
                              redis_client,
                              get_worker_key)

from uuid import uuid4

worker_id = str(uuid4())[:8]

HEARTBEAT_INTERVAL = 5
WORKER_TTL = 15


model_service = ModelService()

def send_heartbeats() -> None:
    while True:

        try:
            worker_data={
                "worker_id": worker_id,
                "status": "alive",
                "last_heartbeat": time.time()
            }

            worker_key = get_worker_key(worker_id)

            redis_client.set(
                get_worker_key(worker_id),
                json.dumps(worker_data),
                ex= WORKER_TTL
            )
            
            print(f"Heartbeat of worker sent: "
                  f"worker= {worker_id},worker_key= {worker_key}")

        except Exception as error:
            print(f"Heartbeat failed for worker "
                  f"{worker_id}: {error}"
            )

        time.sleep(HEARTBEAT_INTERVAL)


def process_jobs() -> None:
    print(f"worker {worker_id} started")
    print("Waiting for the jobs...")

    while True:
        queue_item= redis_client.brpop(
            INFERENCE_QUEUE,
            timeout= 0
        )

        if queue_item is None:
            continue

        _, job_json = queue_item

        job = json.loads(job_json)

        job_id= job["job_id"]
        features= job["features"]

        print(f"worker: {worker_id} Processing job: {job_id}")

        try:
            redis_client.set(
                get_job_key(job_id),
                json.dumps({
                    "job_id": job_id,
                    "status": "processing",
                    "prediction": None,
                    "error": None,
                }),

                ex= 3600,

            )

            prediction= model_service.predict(features)

            redis_client.set(
                get_job_key(job_id),
                json.dumps({
                    "job_id": job_id,
                    "status": "completed",
                    "prediction": prediction,
                    "error": None,
                }),
                ex=3600,
            )

            print(
                f"Completed job: {job_id}\n"
                f"Prediction: {prediction}"

            )

        except Exception as error:
            redis_client.set(
                get_job_key(job_id),
                json.dumps({
                    "job_id": job_id,
                    "status": "failed",
                    "prediction": None,
                    "error": str(error),
                }),
                ex=3600,
            )

            print(f"Job {job_id} failed: {error}")





if __name__ == "__main__":
    heartbeat_thread= threading.Thread(
        target= send_heartbeats,
        daemon= True
    )

    heartbeat_thread.start()

    process_jobs()
