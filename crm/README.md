# CRM Celery Setup Guide

## 1. Install Dependencies

Make sure Redis and all Python packages are installed:

```bash
sudo apt update
sudo apt install redis-server -y
pip install celery django-celery-beat redis gql requests