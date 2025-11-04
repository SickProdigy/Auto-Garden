import urequests as requests
from secrets import secrets

def send_discord_message(message, username="Auto Garden Bot"):
    try:
        data = {
            "content": message,
            "username": username
        }
        
        response = requests.post(secrets['discord_webhook_url'], json=data)
        response.raise_for_status()
        print(f"Discord message sent successfully, code {response.status_code}")
        return True
        
    except Exception as e:
        print(f"Failed to send Discord message: {str(e)}")
        return False
    
    finally:
        if 'response' in locals():
            response.close()