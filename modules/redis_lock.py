from redis import Redis
import uuid


class Lock():
    def acquire(redis: Redis, key, timeout=10, blocking=True):
        id = str(uuid.uuid4())
        if blocking:
            while redis.set(key + ".lock", id, timeout, nx=True) is None:
                pass
            return id
        else:
            if redis.set(key + ".lock", id, timeout, nx=True) is not None:
                return id
            else:
                return None

    def release(redis: Redis, key, id: str):
        if redis.get(key + ".lock").decode("ascii") == id:
            redis.delete(key + ".lock")
        else:
            raise Exception("Lock not acquired")
