# crm/cron.py
from datetime import datetime
from gql.transport.requests import RequestsHTTPTransport
from gql import gql, Client

def log_crm_heartbeat():
    """
    Logs a timestamped heartbeat message to confirm CRM is alive.
    Optionally queries the GraphQL 'hello' field to verify endpoint responsiveness.
    """
    log_file = "/tmp/crm_heartbeat_log.txt"
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive"

    # Optionally query GraphQL 'hello' field to ensure endpoint is up
    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=False,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)

        query = gql("""
            query {
                hello
            }
        """)

        response = client.execute(query)
        hello_message = response.get("hello", "No response from GraphQL.")
        message += f" | GraphQL says: {hello_message}"

    except Exception as e:
        message += f" | GraphQL check failed: {e}"

    # Append log message to file (don’t overwrite)
    with open(log_file, "a") as f:
        f.write(message + "\n")
