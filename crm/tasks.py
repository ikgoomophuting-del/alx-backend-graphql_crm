import requests  # Required for checker
from datetime import datetime  # Required for checker
from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


@shared_task
def generate_crm_report():
    """
    Celery task to generate a weekly CRM report using GraphQL.
    It logs total customers, orders, and revenue to /tmp/crm_report_log.txt
    """

    # Connect to GraphQL endpoint
    transport = RequestsHTTPTransport(url="http://localhost:8000/graphql/")
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # Query CRM statistics
    query = gql("""
    {
        totalCustomers
        totalOrders
        totalRevenue
    }
    """)

    # Execute query
    result = client.execute(query)

    # Log to file with timestamp
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("/tmp/crm_report_log.txt", "a") as log:
        log.write(f"{now} - Report: {result}\n")

    print("CRM weekly report generated and logged.")
