from update_instruments import update_instruments
from flask_apscheduler import APScheduler
import logging

logging.basicConfig(level=logging.INFO)

scheduler = APScheduler()

def start_scheduler(app):
    scheduler.init_app(app)
    scheduler.start()
    logging.info("Scheduler started")

@scheduler.task('interval', id='update_instruments_job', minutes=1)
def scheduled_task():
    logging.info("Début de la tâche planifiée : update_instruments")
    update_instruments()
    logging.info("Fin de la tâche planifiée : update_instruments")
