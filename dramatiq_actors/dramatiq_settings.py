import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware import AsyncIO

broker = RedisBroker(host="redis")
dramatiq.set_broker(broker)
broker.add_middleware(AsyncIO())


