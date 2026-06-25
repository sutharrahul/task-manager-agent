import redis

def redis():
    r = redis.Redis(host="localhost", port=6367,db=0, decode_responses=True)
    return r