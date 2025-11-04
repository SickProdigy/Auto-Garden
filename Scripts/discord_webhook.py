import urequests as requests
try:
    import ujson as json
except Exception:
    import json

from secrets import secrets

def send_discord_message(message, username="Auto Garden Bot"):
    resp = None
    url = secrets.get('discord_webhook_url')
    try:
        payload = {"content": message, "username": username}
        body = json.dumps(payload)
        if isinstance(body, str):
            body = body.encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Content-Length": str(len(body))
        }

        # DEBUG: print exact values being sent
        print("DEBUG: webhook url repr:", repr(url))
        print("DEBUG: body (bytes):", body)
        print("DEBUG: headers:", headers)

        resp = requests.post(url, data=body, headers=headers)

        status = getattr(resp, "status", getattr(resp, "status_code", None))
        text = ""
        try:
            text = resp.text
        except:
            try:
                text = resp.content
            except:
                text = "<no body>"

        print("DEBUG: resp status:", status)
        print("DEBUG: resp body:", text)

        if status and 200 <= status < 300:
            print("Discord message sent")
            return True
        else:
            print("Discord webhook HTTP", status, "body:", text)
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