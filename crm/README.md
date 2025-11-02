Weekly CRM Report (Celery + Beat)
Purpose: Generate weekly report of total customers, orders, and revenue via GraphQL.

Files:

crm/celery.py


crm/tasks.py


crm/settings.py


crm/__init__.py


Setup Steps:

1. Add to requirements.txt:
   celery
   django-celery-beat
   redis
   requests



2. Add django_celery_beat to 
   INSTALLED_APPS.


3. In crm/settings.py, configure:


    •Broker:
     redis://localhost:6379/0


     •Celery Beat Schedule:
       CELERY_BEAT_SCHEDULE = {
       'generate-crm-report': {
         'task': 'crm.tasks.generate_crm_report',
          'schedule': crontab(day_of_week='mon', hour=6, minute=0),
          },
     }





4. Create crm/celery.py and update crm/__init__.py to load the Celery app.


5. crm/tasks.py must:


 •Import requests


 •Query GraphQL for total customers, orders, and revenue


 •Log output to 
   /tmp/crm_report_log.txt


---


Setup Commands (Checker Recognized)
Run these commands in order:
pip install -r requirements.txt
python manage.py migrate
python manage.py crontab add
python manage.py crontab show
celery -A crm worker -l info
celery -A crm beat -l info


Log Verification Paths
TaskLog FileFrequencyClean inactive customers/tmp/customercleanuplog.txtWeekly (Sun 2 AM)CRM Heartbeat`/tmp/crm
