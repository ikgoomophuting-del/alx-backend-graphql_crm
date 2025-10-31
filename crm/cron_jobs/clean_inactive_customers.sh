#!/bin/bash
# clean_inactive_customers.sh
# This script deletes customers with no orders in the past year.
# It runs a Django shell command and logs output to /tmp/customer_cleanup_log.txt

LOG_FILE="/tmp/customer_cleanup_log.txt"
PROJECT_PATH="/path/to/alx-backend-graphql_crm"  # <-- replace with your absolute project path

cd "$PROJECT_PATH" || exit 1

# Activate virtual environment if needed
# source venv/bin/activate

/usr/bin/python3 manage.py shell <<EOF >> "$LOG_FILE" 2>&1
from datetime import timedelta, date
from crm.models import Customer

cutoff_date = date.today() - timedelta(days=365)
inactive_customers = Customer.objects.exclude(orders__order_date__gte=cutoff_date)

count = inactive_customers.count()
inactive_customers.delete()
print(f"Deleted {count} inactive customers with no orders since {cutoff_date}.")
EOF

echo "Customer cleanup completed at \$(date)" >> "$LOG_FILE"
