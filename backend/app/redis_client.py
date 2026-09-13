import redis 

redis_client= redis.Redis(
    host= "localhost",
    port= 6379,
    decode_responses= True,
    socket_timeout= None
)

INFERENCE_QUEUE= "inference_jobs"

PROCESSING_QUEUE= "inference_processing"

PROCESSING_QUEUE_PREFIX= "inference_processing"

def get_job_key(job_id: str) -> str:
    return f"job:{job_id}"

def get_worker_key(worker_id: str) -> str:
    return f"worker:{worker_id}"

def get_processing_queue(worker_id: str) -> str:
    return f"{PROCESSING_QUEUE_PREFIX}:{worker_id}"

