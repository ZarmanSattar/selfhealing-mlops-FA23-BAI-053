import time
import requests
from prometheus_client import start_http_server, Gauge

APP_URL = "http://localhost:32500/api/latest-confidence"
POLL_INTERVAL = 5
EXPORTER_PORT = 8000

prediction_confidence_score = Gauge(
    "prediction_confidence_score",
    "Latest prediction confidence score from the sentiment API"
)

def poll():
    while True:
        try:
            resp = requests.get(APP_URL, timeout=3)
            resp.raise_for_status()
            confidence = resp.json().get("confidence", 1.0)
        except Exception:
            confidence = 1.0
        prediction_confidence_score.set(confidence)
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    start_http_server(EXPORTER_PORT)
    poll()
