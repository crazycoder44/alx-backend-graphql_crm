#!/bin/bash
# crm/cron_jobs/clean_inactive_customers.sh
# Deletes customers with no orders in the last 365 days and logs the number removed.

# OPTIONAL: set PYTHON_BIN to your virtualenv python for cron to use
# Example: /home/username/alx-backend-graphql-crm/venv/bin/python
# If left empty, script will call "python manage.py" which uses system python.
PYTHON_BIN="/mnt/c/Users/ADMIN/Documents/ALX/BE ProDev/alx-backend-graphql_crm/alx_backend_graphql_crm/venv/bin/python"

# Resolve the script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Walk up to find manage.py (search up to 6 levels)
PROJ_DIR="$SCRIPT_DIR"
for i in {1..6}; do
  if [ -f "$PROJ_DIR/manage.py" ]; then
    break
  fi
  PROJ_DIR="$(dirname "$PROJ_DIR")"
done

if [ ! -f "$PROJ_DIR/manage.py" ]; then
  echo "$(date -Iseconds) ERROR: manage.py not found (searched up from $SCRIPT_DIR)" >&2
  exit 1
fi

cd "$PROJ_DIR" || exit 1

# Choose python command
if [ -n "$PYTHON_BIN" ] && [ -x "$PYTHON_BIN" ]; then
  PY_CMD="$PYTHON_BIN"
else
  PY_CMD="python"
fi

"$PY_CMD" manage.py shell <<'PY'
from django.utils import timezone
from datetime import timedelta
from django.db.models import Max, Q
from django.conf import settings

# IMPORTANT: adjust the import below if your Customer model lives elsewhere
try:
    from crm.models import Customer
except Exception as e:
    raise SystemExit(f"Could not import Customer: {e}")

cutoff = timezone.now() - timedelta(days=365)

# NOTE: change this annotation if your Order related_name or timestamp field differs:
# e.g. 'orders__created_at' or 'order_set__created'
last_order_field = 'orders__order_date'  # <-- edit if necessary

qs = Customer.objects.annotate(last_order=Max(last_order_field)).filter(Q(last_order__lt=cutoff) | Q(last_order__isnull=True))

count = qs.count()
qs.delete()

with open('/tmp/customer_cleanup_log.txt','a') as f:
    f.write(f"{timezone.now().isoformat()} - Deleted {count} inactive customers\n")
PY
# print
