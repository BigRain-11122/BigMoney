"""Celery app. Broker = Redis on master."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from celery import Celery
except ImportError:
    Celery = None

from config import REDIS


broker_url = f"redis://{REDIS.host}:{REDIS.port}/{REDIS.db}"

app = None
if Celery is not None:
    app = Celery(
        "quant_backtest",
        broker=broker_url,
        backend=broker_url,
    )
    app.conf.update(
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        task_default_queue=REDIS.backtest_queue,
        result_expires=86400,
        task_track_started=True,
    )
