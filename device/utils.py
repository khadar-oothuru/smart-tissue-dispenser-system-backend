import requests

def send_push_notification(expo_token, title, body, data=None):
    payload = {
        "to": expo_token,
        "sound": "default",
        "title": title,
        "body": body,
        "data": data or {}
    }

    response = requests.post(
        "https://exp.host/--/api/v2/push/send",
        json=payload,
        headers={"Content-Type": "application/json"}
    )

    return response.json()
