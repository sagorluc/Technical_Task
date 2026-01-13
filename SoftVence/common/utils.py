from redis import Redis
import uuid

r = Redis()

def acquire_lock(key, ttl=10):
    token = str(uuid.uuid4())
    if r.set(key, token, nx=True, ex=ttl):
        return token
    return None

def release_lock(key, token):
    if r.get(key) == token.encode():
        r.delete(key)
