#!/usr/bin/env python

import datetime
import logging
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Configure logging
LOG_FILE = "/tmp/order_reminders_log.txt"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)

def fetch_recent_orders():
    """
    Fetch orders placed within the last 7 days via GraphQL query.
    """
    # GraphQL endpoint
    endpoint = "http://localhost:8000/graphql"

    # Set up GraphQL transport
    transport = RequestsHTTPTransport(
        url=endpoint,
        verify=False,
        retries=3,
    )

    client = Client(transport=transport, fetch_schema_from_transport=True)

    # Calculate date range
    today = datetime.date.today()
    seven_days_ago = today - datetime.timedelta(days=7)

    # GraphQL query
    query = gql(
        """
        query RecentOrders($startDate: Date!) {
            orders(filter: { orderDate_Gte: $startDate }) {
                id
                customer {
                    email
                }
                orderDate
            }
        }
        """
    )

    params = {"startDate": seven_days_ago.isoformat()}

    # Execute query
    result = client.execute(query, variable_values=params)
    return result.get("orders", [])


def log_order_reminders():
    """
    Logs each order’s ID and customer email.
    """
    try:
        orders = fetch_recent_orders()

        if not orders:
            logging.info("No recent orders found.")
        else:
            for order in orders:
                logging.info(
                    "Order ID: %s | Customer Email: %s",
                    order.get("id"),
                    order.get("customer", {}).get("email"),
                )

        print("Order reminders processed!")

    except Exception as e:
        logging.error(f"Error processing order reminders: {e}")
        print(f"Error: {e}")


if __name__ == "__main__":
    log_order_reminders()
  
