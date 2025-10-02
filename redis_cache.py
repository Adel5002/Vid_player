import redis

# ------------------ Redis Cache ------------------
cache = redis.Redis(host="redis", port=6379, db=0)