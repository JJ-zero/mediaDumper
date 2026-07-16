from .process_base import ProcessBase
from pathlib import Path
import shutil

# Device config example:
"""
{
    "process": "extract_video",
    "source_folder": "DCIM/VIDEO",
    "order": "name",
    "checkpoint": "VIDEO420.AVI",
    "self_checkpoint_reset": true
}
"""


class SimpleCopy(ProcessBase):
    @classmethod
    def run(cls, config, device_config, device_path: Path):
        if device_config.get("order", "name") != "name":
            raise NotImplementedError("Only order by name is supported for now.")
        target_string = config.get("target", "/tmp")
        target = Path(target_string.format(**cls.prepare_nametemplate_data()))
        target.mkdir(parents=True, exist_ok=True)
        ignore_meta = device_config.get("ignore_meta", True)
        device_path = Path(device_path)
        source_string = device_config.get("source_folder", ".")
        source: Path = device_path / source_string

        found_files = [
            file
            for file in source.iterdir()
            if file.is_file()
        ]
        found_files.sort(key=lambda x: x.name)

        if found_files and found_files[-1].name == device_config.get("checkpoint", ""):
            return found_files[-1].name

        files = [
            file
            for file in found_files
            if file.name > device_config.get("checkpoint", "")
            and (
                not ignore_meta or not file.name.startswith(".")
            )  # This is overcomplicated, rework later
        ]

        if not files:
            if not device_config.get("self_checkpoint_reset", False):
                return
            files = [file for file in source.iterdir() if file.is_file()]

        for index, file in enumerate(files):
            print(f"Copying {file.name} [{index}/{len(files)}] to {target}")
            target_file = target / file.name
            if target_file.exists():
                print(f"File {target_file} already exists, skipping.")
                continue
            shutil.copy(file, target / file.name)
        return files[-1].name
