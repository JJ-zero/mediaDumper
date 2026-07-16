import subprocess
import json
from pathlib import Path
from time import sleep

from processes.process_base import ProcessBase
from processes.simple_copy import SimpleCopy
from helpers.home_assistant import HomeAssistant
import argparse


class MediaDumper:
    """
    This class is overall way to dump files from external media devices as SD cards, USB sticks, etc.
    """

    def __init__(self, config_path=Path(__file__).parent / "config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.script_registry: dict[str, type[ProcessBase]] = {
            "SimpleCopy": SimpleCopy,
        }
        if HomeAssistant.CONFIG_FIELD in self.config:
            self.home_assistant = HomeAssistant(config=self.config.get(HomeAssistant.CONFIG_FIELD, {}))
        else:
            self.home_assistant = None

    def _load_config(self):
        """
        Load the configuration file.
        """
        with open(self.config_path, "r") as f:
            return json.load(f)

    def get_devices(self):
        """
        Get all devices that are connected to the system.
        """
        devices = subprocess.run(
            [
                "lsblk",
                "-J",
                "-o",
                "NAME,SIZE,SERIAL,TYPE,MOUNTPOINTS,PATH,LABEL,HOTPLUG,MODEL,STATE",
            ],
            stdout=subprocess.PIPE,
        )
        devices = [
            d
            for d in json.loads(devices.stdout).get("blockdevices")
            if d["name"] not in self.config.get("ignored", [])
        ]
        return devices

    def notify(self, message):
        try:
            if self.home_assistant:
                self.home_assistant.notify(message)
        except Exception as e:
            print(f"Failed to send notification: {e}")

    # Pre and Post Processing hooks are here for now mostly as a placeholders. They will get new arguments in the
    # future to allow for more complex processing. More changes will be needed for valid pre and post processing hooks.

    def _preprocess(self):
        pass
    
    def _postprocess(self):
        pass

    def mount_device(self, path, mount_path="sd"):
        """
        Mount the device to the system.
        """
        print(f"Mounting device: {path}")
        subprocess.run(["pmount", path, mount_path])

    def unmount_device(self, mount_path="sd"):
        """
        Unmount the device from the system.
        """
        print(f"Unmounting device: {mount_path}")
        # TODO: Add error handling (if device is busy and cannot be unmounted)
        subprocess.run(["pumount", mount_path])

    def load_device_config(self, path: Path) -> None | dict:
        """
        Load the configuration for the device.
        """
        config_file = path / "dump.json"
        if config_file and config_file.exists() and config_file.is_file():
            with open(config_file, "r") as f:
                return json.load(f)

    def process_device(self, device):
        if "children" in device:
            for child in device["children"]:
                self.process_device(child)
            return
        mount_points = device.get("mountpoints", [])
        if mount_points and mount_points[0]:
            print(f"Device: {device['name']}")
            print(f"Mountpoint: {device['mountpoints']}")
            print("----------------")
            return
        if device.get("size", "0B") == "0B":
            print(f"Device: {device['name']}")
            print("Device is empty.")
            print("----------------")
            return
        print(f"Device: {device['name']}")
        self.mount_device(device["path"])

        dc = self.load_device_config(Path("/media/sd"))
        if not dc:
            print("No configuration found for the device.")
            return

        process_name = dc.get("process")
        process = self.config.get("processes", {}).get(process_name)
        if not process:
            print(f"Process {process_name} not found.")
            return

        if dc.get("name"):
            device["name"] = dc.get("name")

        if process.get("enabled", True) is False:
            print(f"Process {process_name} is disabled.")
            self.notify(f"Device {device['name']} requires currently disabled process '{process_name}'.")
            return

        script: type[ProcessBase] | None = self.script_registry.get(process.get("script"))

        if script is None:
            print(f"Script {process.get('script')} not found.")
            self.notify(f"Device {device['name']} requires unknown script '{process.get('script')}'.")
            return

        self.notify(f"Device connected: {device['name']}")
        try:
            self._preprocess()
            new_checkpoint = script.run(process, dc, Path("/media/sd"))
            if new_checkpoint:
                dc["checkpoint"] = new_checkpoint
                with open(Path("/media/sd") / "dump.json", "w") as f:
                    json.dump(dc, f, indent=4)
        finally:
            self._postprocess()
            self.unmount_device(device["path"])
            self.notify(f"Device disconnected: {device['name']}")

    def run(self):
        """
        Run the media dumper.
        """
        devices = self.get_devices()
        for device in devices:
            self.process_device(device)

    def run_watchdog(self):
        """
        Run the watchdog for the media dumper.
        """

        last_run_devices = []

        watchdog_config = self.config.get("watchdog", {})
        sleep_time_minimum = watchdog_config.get("minimal_interval", 10)
        sleep_time_maximum = watchdog_config.get("maximal_interval", 300)

        sleep_time = sleep_time_minimum

        while True:
            try:
                devices = self.get_devices()
                for device in devices:
                    if device not in last_run_devices:
                        self.process_device(device)
                        sleep_time = sleep_time_minimum  # Reset sleep time after processing a new device
                last_run_devices = devices
            except Exception as e:
                print(f"Error: {e}")
                self.notify(f"MediaDumper encountered an error: {str(type(e).__name__)}")
            finally:
                sleep(sleep_time)
                sleep_time = min(round(sleep_time * 1.4), sleep_time_maximum)  # Exponential backoff up to maximal interval


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--watchdog",
        action="store_true",
        help="Runs forever and checks for new devices.",
        default=False,
    )

    parsed = parser.parse_args()

    md = MediaDumper()
    if parsed.watchdog:
        md.run_watchdog()
    else:
        md.run()
