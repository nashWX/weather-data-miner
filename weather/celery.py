from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "weather.settings")

app = Celery("weather", broker=settings.CELERY_BROKER_URL)

app.config_from_object("django.conf:settings")

app.autodiscover_tasks()

# app.conf.CELERYBEAT_SCHEDULE = {
#     'fetch-lots-from-goszakup-every-20-minutes': {
#         'task': 'lots.tasks.fetch_lots_from_goszakup',
#         'schedule': crontab(minute='0', hour='*/1', day_of_week="*"), #60minutes

#     },
#     'remove-expired-lots-every-thirty-minutes': {
#         'task': 'lots.tasks.removeExpiredLots',
#         'schedule': crontab(minute='30', hour='*', day_of_week="*"), #60minutes

#     },
#     'update_existing_region_location': {
#         'task': 'lots.tasks.update_existing_lots_region_location',
#         'schedule': crontab(minute='*/30'),
#     },
#     "check_task_before_3days_of_expire_tarif": {
#         "task": "users.tasks.task_before_3days_of_expire_tarif",
#         "schedule": crontab(hour="6,18", minute=0)
#     },
#     "check_task_after_expire_tarif": {
#         "task": "users.tasks.task_after_expire_tarif",
#         "schedule": crontab(hour="23", minute=59)
#     },
#     "check_task_after_3days_of_expire_tarif": {
#         "task": "users.tasks.task_after_3days_of_expire_tarif",
#         "schedule": crontab(hour="14", minute=0)
#     }
# }
if __name__ == "__main__":
    app.start()

