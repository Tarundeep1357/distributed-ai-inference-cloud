import redis 

redis_client= redis.Redis(
    host= "localhost",
    port= 6379,
    decode_responses= True
)

INFERENCE_QUEUE= "inference_job"

def get_job_key(job_id: str) -> str:
    return f"job:{job_id}"