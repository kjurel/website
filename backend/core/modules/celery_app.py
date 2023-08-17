from src.settings.config import settings
from celery import Celery

celery_app = Celery(
    "celery_worker", backend=settings.REDIS_URL, broker=settings.RABBIT_URL
)
celery_app.config_from_object("app.settings.config_celery")
celery_app.autodiscover_tasks(settings.get_cl_app_list(), None)
