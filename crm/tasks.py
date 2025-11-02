from datetime import datetime
from celery import shared_task
from gql.transport.requests import RequestsHTTPTransport
from gql import gql, Client

@shared_task
def generate_crm_report():
    """
    Generates a weekly CRM report of total customers, orders, and revenue.
    Logs to /tmp/crm_report_log.txt.
    """
    log_file = "/tmp/crm_report_log.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    query = gql("""
    query {
        customers {
            id
        }
        orders {
            id
            totalAmount
        }
    }
    """)

    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=False,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)
        response = client.execute(query)

        total_customers = len(response.get("customers", []))
        orders = response.get("orders", [])
        total_orders = len(orders)
        total_revenue = sum(order.get("totalAmount", 0) for order in orders)

        report = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, {total_revenue} revenue"

    except Exception as e:
        report = f"{timestamp} - ERROR generating report: {e}"

    with open(log_file, "a") as f:
        f.write(report + "\n")

    return report
    
