# crm/cron.py
from datetime import datetime
import requests
from gql.transport.requests import RequestsHTTPTransport
from gql import gql, Client

def log_crm_heartbeat():
    """
    Logs a heartbeat timestamp to /tmp/crm_heartbeat_log.txt
    Format: DD/MM/YYYY-HH:MM:SS CRM is alive
    Optionally checks GraphQL hello field at http://localhost:8000/graphql
    """
    ts = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    line = f"{ts} CRM is alive\n"
    try:
        # append heartbeat
        with open("/tmp/crm_heartbeat_log.txt", "a") as f:
            f.write(line)

        # Optional GraphQL check — non-fatal
        try:
            graphql_url = "http://localhost:8000/graphql"
            query = '{"query":"{ hello }"}'
            resp = requests.post(graphql_url, data=query, headers={"Content-Type":"application/json"}, timeout=3)
            # If you want to log the check result, uncomment the following lines:
            # with open("/tmp/crm_heartbeat_log.txt", "a") as f:
            #     f.write(f"{ts} GraphQL check status: {resp.status_code}\\n")
        except Exception:
            # ignore GraphQL check errors — still keep heartbeat
            pass

    except Exception as e:
        # Safe fallback if writing fails (do not crash cron)
        try:
            with open("/tmp/crm_heartbeat_log.txt", "a") as f:
                f.write(f"{ts} CRM heartbeat write failed: {e}\\n")
        except Exception:
            # last resort: ignore
            pass