import json 
import time 

from app.redis_client import (
    redis_client,
    INFERENCE_QUEUE,
    PROCESSING_QUEUE_PREFIX,
    get_job_key,
    get_processing_queue,
    get_worker_key)

PROCESSING_QUEUE_PREFIX = "inference_processing"

def get_processing_queue():

    queue= []

    for key in redis_client.scan_iter(f"{PROCESSING_QUEUE_PREFIX}:*"):
        queue.append(key)

    return queue

def recover_dead_workers(queue_names: str):

    worker_id= queue_names.split(":")[-1]

    worker_key= get_worker_key(worker_id)

    if redis_client.exists(worker_key):
        return 

    print(f"Recovering dead worker: {worker_id}")

    while True:

        job_json= redis_client.rpop(queue_names)

        if job_json is None:
            break

        job= json.loads(job_json)

        print(f"Recovering job: {job['job_id']} from dead worker: {worker_id}")

        redis_client.lpush(INFERENCE_QUEUE, json.dumps(job))

        redis_client.set(
            f"job:{job['job_id']}",
            json.dumps(
                {
                    "job_id": job["job_id"],
                    "status": "queued",
                    "prediction": None,
                    "error": None
                }

            ),
            ex= 3600
        )


def recovery_loop():

    print("Recovery service started")

    while True:

        processing_queues= get_processing_queue()

        for queue in processing_queues:
            recover_dead_workers(queue)


        time.sleep(30)

    
if __name__ == "__main__":
    recovery_loop()