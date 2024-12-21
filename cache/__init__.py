import redis
import os
from dotenv import load_dotenv

load_dotenv()

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"), 
    port=os.getenv("REDIS_PORT"), 
    db=os.getenv("REDIS_DB"), 
    #password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True
)
