import dramatiq
from dramatiq.brokers.redis import RedisBroker

broker = RedisBroker(host="redis")
dramatiq.set_broker(broker)


