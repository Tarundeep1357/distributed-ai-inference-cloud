import redis 

redis_client= redis.Redis(
    host= "localhost",
    port= 6379,
    decode_responses= True,
    socket_timeout= None
)

INFERENCE_QUEUE= "inference_jobs"

def get_job_key(job_id: str) -> str:
    return f"job:{job_id}"