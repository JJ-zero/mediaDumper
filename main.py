import subprocess
import json
from pathlib import Path
from time import sleep

from process_base import ProcessBase
from simple_copy import SimpleCopy


config_path = Path(__file__).parent / "config.json"


class MediaDumper:
    """
    This class is overall way to dump files from external media devices as SD cards, USB sticks, etc.
    """

    def __init__(self):
        self.config = self.load_config()
        self.script_registry: dict[ProcessBase] = {
            "SimpleCopy": SimpleCopy,
        }

    def load_config(self):
        """
        Load the configuration file.
        """
        with open(config_path, "r") as f:
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

    def load_device_config(self, path: Path):
        """
        Load the configuration for the device.
        """
        if path / "dump.json":
            with open(path / "dump.json", "r") as f:
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
        script: ProcessBase = self.script_registry.get(process.get("script"))

        try:
            new_checkpoint = script.run(process, dc, Path("/media/sd"))
            if new_checkpoint:
                dc["checkpoint"] = new_checkpoint
                with open(Path("/media/sd") / "dump.json", "w") as f:
                    json.dump(dc, f, indent=4)
        finally:
            self.unmount_device(device["name"])

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

        while True:
            devices = self.get_devices()
            for device in devices:
                if device not in last_run_devices:
                    self.process_device(device)
            last_run_devices = devices
            sleep(60)


if __name__ == "__main__":
    md = MediaDumper()
    md.run()
