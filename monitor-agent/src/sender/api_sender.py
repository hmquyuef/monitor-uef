import httpx
from src.config.settings import SERVER_URL, API_KEY, AGENT_NAME
import datetime
from loguru import logger

def send_metrics(payload):
    url = f"{SERVER_URL}/api/metrics"
    headers = {
        "Authorization": f"ApiKey {API_KEY}",
        "Content-Type": "application/json"
    }

    # Bổ sung thông tin định danh agent
    payload["agent_name"] = AGENT_NAME
    payload["collected_at"] = datetime.datetime.utcnow().isoformat() + "Z"

    try:
        # follow_redirects=True: tự động theo 301/302 khi Nginx redirect HTTP -> HTTPS
        with httpx.Client(timeout=10.0, follow_redirects=True, verify=False) as client:
            response = client.post(url, json=payload, headers=headers)
            if response.status_code in (200, 201):
                logger.success(f"Metrics sent successfully for {AGENT_NAME}")
                return response.json().get("config", {})
            else:
                logger.error(f"Failed to send metrics: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        logger.error(f"Error connecting to server: {str(e)}")
        return False
