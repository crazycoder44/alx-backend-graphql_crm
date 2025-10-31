import datetime
from celery import shared_task
from django.utils import timezone
from graphene_django.utils.testing import graphql_query

from crm.schema import schema  # your GraphQL schema

@shared_task
def generate_crm_report():
    """
    Generates a CRM report of total customers, orders, and revenue.
    Logs the report to /tmp/crm_report_log.txt
    """
    query = '''
    {
        allCustomers {
            totalCount
        }
        allOrders {
            totalCount
            edges {
                node {
                    totalAmount
                }
            }
        }
    }
    '''

    result = schema.execute(query)
    if result.errors:
        log = f"{timezone.now()} - Error generating report: {result.errors}\n"
    else:
        customers = result.data['allCustomers']['totalCount']
        orders = result.data['allOrders']['totalCount']
        total_revenue = sum(float(edge['node']['totalAmount']) for edge in result.data['allOrders']['edges'])

        log = f"{timezone.now():%Y-%m-%d %H:%M:%S} - Report: {customers} customers, {orders} orders, {total_revenue} revenue\n"

    with open('/tmp/crm_report_log.txt', 'a') as f:
        f.write(log)
