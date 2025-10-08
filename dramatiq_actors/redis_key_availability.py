from dramatiq.middleware import TimeLimit
from sqlmodel import Session

import dramatiq
import time

from db.crud import get_user_by_username
from db.db import engine
from dramatiq_actors.dramatiq_settings import broker
from redis_cache import cache

from dramatiq_actors import dramatiq_settings

for mw in list(broker.middleware):
    if isinstance(mw, TimeLimit):
        broker.middleware.remove(mw)

@dramatiq.actor(queue_name="light_tasks")
def watch_expired_refresh_tokens():
    cache.config_set("notify-keyspace-events", "Ex")

    pubsub = cache.pubsub()
    pubsub.psubscribe("__keyevent@0__:expired")

    print("👁️‍🗨️  Watching Redis expired keys...")

    for message in pubsub.listen():
        if message["type"] == "pmessage":
            expired_key = message["data"].decode()

            if expired_key == 'anime':
                print(expired_key, ' ⚠️')

            if expired_key.startswith("refresh:"):
                username = expired_key.split("refresh:")[-1]
                print(f"🧨 Refresh token expired for user: {username}")

                with Session(engine) as session:
                    user = get_user_by_username(session, username)

                    user.disabled = True
                    session.add(user)
                    session.commit()
                    session.refresh(user)

        time.sleep(0.1)