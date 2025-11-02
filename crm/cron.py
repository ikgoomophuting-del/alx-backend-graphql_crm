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


def update_low_stock():
    """
    Executes the UpdateLowStockProducts GraphQL mutation every 12 hours
    and logs updates to /tmp/low_stock_updates_log.txt.
    """
    log_file = "/tmp/low_stock_updates_log.txt"
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} | Low stock update started."

    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=False,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)

        mutation = gql("""
            mutation {
                updateLowStockProducts {
                    success
                    updatedProducts {
                        name
                        stock
                    }
                }
            }
        """)

        response = client.execute(mutation)
        result = response.get("updateLowStockProducts", {})
        updated_products = result.get("updatedProducts", [])

        message += f" | {result.get('success', 'Mutation executed.')}"
        for p in updated_products:
            message += f" | {p['name']} -> Stock: {p['stock']}"

    except Exception as e:
        message += f" | ERROR: {e}"

    with open(log_file, "a") as f:
        f.write(message + "\n")
        
