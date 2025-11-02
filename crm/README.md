CRM GraphQL Automation – README
Overview

This project automates key maintenance tasks in the CRM GraphQL system using:

Shell scripts and cron jobs
Django-crontab for scheduled jobs
Celery and Celery Beat for periodic reporting
GitHub Actions for CI/CD


Requirements
Redis
Celery
Django Celery Beat
{Redis installed and running on localhost:6379}

Installation
sudo apt install redis-server
pip install -r requirements.txt
python manage.py migrate
celery -A crm worker -l info
celery -A crm beat -l info
cat /tmp/crm_report_log.txt
