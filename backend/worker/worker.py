import json 

from app.model_service import ModelService

from app.redis_client import (INFERENCE_QUEUE,
                              get_job_key, 
                              redis_client)

ModelService = ModelService()

def process_jobs() -> None:
    print("Interference worker started")
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
        features= jon["features"]

        print(f"Processing job: {job_id}")

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
    process_jobs()
