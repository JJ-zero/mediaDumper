import requests

class HomeAssistant:
    CONFIG_FIELD = "home_assistant"

    def __init__(self, config):
        if not config.get('token'):
            raise ValueError("No token provided.")

        if not config.get('devices'):
            raise ValueError("No devices provided.")
        self.devices = config.get('devices')

        self.headers = {"Authorization": f"Bearer {config.get('token')}"}
        url = config.get("url", "http://localhost:8123")
        self.url_base = f"{url}/api/"
        self.timeout = config.get("timeout", 15)

    def notify(self, message):
        if not self.devices:
            raise ValueError("No devices configured for notification.")
        for device in self.devices:
            self._send_notification(device, message)

    def _send_notification(self, device, message):
        url = f"{self.url_base}services/notify/{device}"
        data = {"message": message}
        requests.post(url, headers=self.headers, json=data, timeout=self.timeout)