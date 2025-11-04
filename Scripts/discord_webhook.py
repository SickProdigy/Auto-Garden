import urequests as requests
import ujson
from secrets import secrets

def send_discord_message(message, username="Auto Garden Bot"):
    response = None
    try:
        data = {
            "content": message,
            "username": username
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            secrets['discord_webhook_url'],
            data=ujson.dumps(data),
            headers=headers
        )
        status = getattr(response, "status", getattr(response, "status_code", None))
        if status and 200 <= status < 300:
            print(f"Discord message sent successfully, code {status}")
            return True
        else:
            print(f"Discord webhook error: HTTP {status}, body: {getattr(response, 'text', '')}")
            return False
    except Exception as e:
        print(f"Failed to send Discord message: {str(e)}")
        return False
    finally:
        if response:
            try:
                response.close()
            except:
                pass