import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.results.backends import RedisBackend
from dramatiq.results import Results
from dramatiq.middleware import AsyncIO

result_backend = RedisBackend(host="redis")
broker = RedisBroker(host="redis")
broker.add_middleware(AsyncIO())
broker.add_middleware(Results(backend=result_backend))
dramatiq.set_broker(broker)

