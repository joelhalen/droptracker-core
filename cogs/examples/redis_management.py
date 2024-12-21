"""
This file is an example of how to interact with the Redis cache which maintains player and group stats. 

Notes:
"""

from cache import redis_client

async def example_redis_interaction():
    # We can use the redis_client to interact with the cache.
    # This is a simple key-value store, so we can set and get values.
    await redis_client.set("example_key", "example_value")
    value = await redis_client.get("example_key")
    print(value)

