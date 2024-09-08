import requests

class HomeAssistant:
    CONFIG_FIELD = "home_assistant"

    def __init__(self, config):
        if not config.get('token'):
            raise ValueError("No token provided.")

        self.headers = {"Authorization": f"Bearer {config.get('token')}"}
        url = config.get("url", "http://localhost:8123")
        self.url_base = f"{url}/api/"

    def notify(self, message):
        device = "mobile_app_fusion"
        url = f"{self.url_base}services/notify/{device}"
        data = {"message": message}
        requests.post(url, headers=self.headers, json=data)