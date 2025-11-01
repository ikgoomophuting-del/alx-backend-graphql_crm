# crm/cron.py
from datetime import datetime
import requests

def log_crm_heartbeat():
    """Logs a heartbeat message confirming CRM is alive."""
    log_file = "/tmp/crm_heartbeat_log.txt"
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive\n"

    # Write (append) to log file
    with open(log_file, "a") as f:
        f.write(message)

    # Optional: check GraphQL endpoint (for health check)
    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": "{ hello }"},
            timeout=5
        )
        if response.status_code == 200:
            with open(log_file, "a") as f:
                f.write(f"{timestamp} GraphQL endpoint responded OK\n")
        else:
            with open(log_file, "a") as f:
                f.write(f"{timestamp} GraphQL check failed with status {response.status_code}\n")
    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"{timestamp} GraphQL check failed: {str(e)}\n")
  
