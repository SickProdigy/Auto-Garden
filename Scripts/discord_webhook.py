import urequests as requests
try:
    import ujson as json
except Exception:
    import json

from secrets import secrets

def send_discord_message(message, username="Auto Garden Bot"):
    resp = None
    try:
        payload = {"content": message, "username": username}
        body = json.dumps(payload)
        if isinstance(body, str):
            body = body.encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Content-Length": str(len(body))
        }
        resp = requests.post(secrets['discord_webhook_url'], data=body, headers=headers)

        status = getattr(resp, "status", getattr(resp, "status_code", None))
        body_text = ""
        try:
            body_text = resp.text
        except Exception:
            try:
                body_text = resp.content
            except Exception:
                body_text = ""

        if status and 200 <= status < 300:
            print("Discord message sent")
            return True
        else:
            print("Discord webhook HTTP", status, "body:", body_text)
            return False
    except Exception as e:
        print("Failed to send Discord message:", e)
        return False
    finally:
        if resp:
            try:
                resp.close()
            except:
                pass