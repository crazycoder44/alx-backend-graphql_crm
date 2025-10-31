# CRM Celery and Celery Beat Setup

## Install Redis and dependencies

Install Redis server and required Python packages:

```bash
sudo apt update
sudo apt install redis-server -y
pip install celery django-celery-beat redis gql requests
```

## Run migrations (python manage.py migrate)

Apply database migrations to set up required tables:

```bash
python manage.py migrate
```

## Start Celery worker (celery -A crm worker -l info)

Start the Celery worker to handle background tasks:

```bash
celery -A crm worker -l info
```

## Start Celery Beat (celery -A crm beat -l info)

Start Celery Beat to schedule periodic tasks:

```bash
celery -A crm beat -l info
```

## Verify logs in /tmp/crm_report_log.txt

After Celery Beat runs, verify that reports are logged in /tmp/crm_report_log.txt:

Each log entry should follow this format:

```bash
2025-10-31 06:00:00 - Report: X customers, Y orders, Z revenue
```

### Notes

- Redis must be running on redis://localhost:6379/0.

- The task generate_crm_report runs weekly on Monday at 6 AM.

- You can manually test Celery by calling:

```bash
python manage.py shell
>>> from crm.tasks import generate_crm_report
>>> generate_crm_report.delay()
```


---
