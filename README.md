# MediaDumper
Simple tool to copy data from any connected media device into a local folder.

## Is this for me?
Probably not, to be honest, but if you have linux PC or server and often need to copy data from various media devices
(like SD cards or USB drives), this tool might be useful for you. I'm making this mainly for fast dumping of videos
from my drones, but if you are a cinematographer or photographer, you might find this useful too.

## How to use it?
1. Clone or download this repository
0. Check if `lsblk` command is available on your system. If not, install it.
0. Check if `pmount` package is available on your system. It's probably not, so don't forget to install it. You need
the `pmount` and `pumount` commands to be available to the user running the script.
0. Create your config file. You can start by copying `config_template.json` to `config.json` and editing it.
    - `ignored` is a list of drives that are fully ignored by the script when looking for media devices.
    - `processes` is a dictionary of process definitions that can be run over found media drives. The key of each
    entry is used as the process name and you can choose it freely.
        - `script` is the only required field in the process definition. It's the name of the process class to be run.
        - `enabled` is optional (`true` by default). Set it to `false` to disable a process without removing its config.
        - For other fields, check the documentation of the process class you want to use.
0. Create config on your media device as `dump.json`. You can start by copying `dump_template.json` to `dump.json` and
editing it.
    - `process` - name of the process to be run on this media device. It must be defined in `config.json`.
    - `checkpoint` - Any kind of structure that the selected process uses to store information about already processed files.
    - For other fields, check the documentation of the process class you want to use.
0. Run the script with `python3 main.py` for one-time processing, or `python3 main.py --watchdog` to keep checking for new devices every 60 seconds.

## Processes
### Simple Copy
Script name: `SimpleCopy`
#### `config.json` fields
- `target` - Template for target path. You can use `{}` to insert current date and time in different formats.
For example: `~/Videos/{date}`
    - `{date}` - Current date in format `YYYY-MM-DD`
    - `{dateRaw}` - Current date in format `YYYYMMDD`
    - `{time}` - Current time in format `HH-MM-SS`
    - `{datetime}` - Current date and time in format `YYYY-MM-DD_HH-MM-SS`
#### `dump.json` fields
- `source_folder` - Path to folder on media device that should be copied.
- `order` - Way the files should be ordered and compared to find new files. For now only supports `name`.
- `self_checkpoint_reset` - Attempt to detect if the media device was cleaned and reset the checkpoint if so.
- `ignore_meta` - If set to `true` (default), files starting with `.` are ignored. 
- `checkpoint` - Last processed file name used to continue from previous run. This field is updated automatically by
the script and it's the thing that keeps track of already processed files. You can set it to empty string to process
all files on the first run.

## Notifications
### Home assistant
For bigger transfers, it might be useful to get notified when the transfer is finished. Exactly for those cases,
there is a simple Home Assistant subsystem. It uses the Home Assistant notify service to send notifications to your mobile device.
To enable it, add `home_assistant` field to your `config.json` with following structure:

```json
"home_assistant": {
    "url": "http://homeassistant.local:8123",
    "token": "YOUR_LONG_LIVED_ACCESS_TOKEN",
    "devices": ["mobile_app_pixel"],
    "timeout": 15
}
```

| Field      | Type    | Required | Description |
| ---------- | ------- | -------- | ----------- |
| `token`    | string  | ✅ | Home Assistant long-lived access token. |
| `devices`  | array   | ✅ | List of notify services (for example `mobile_app_pixel`). |
| `url`      | string  | ❌ | Home Assistant URL. Default is `http://localhost:8123`, ideal if HA runs on the same machine.|
| `timeout`  | integer | ❌ | Request timeout in seconds. Default is `15`. |


## Do you want to help?
This is my personal project and I spend my personal time on it. That means I may not have time to implement everything.
If you are missing some feature or found a bug, feel free to create an issue or even a pull request.
If you are happy with the project and want to support it, you can buy me a tea. Otherwise, just
let me know that you like and / or use it. It's good motivation to keep going.


[![Buy me a coffee](https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20tea&emoji=🍵&slug=jj.0&button_colour=FFDD00&font_colour=000000&font_family=Arial&outline_colour=000000&coffee_colour=ffffff)](https://buymeacoffee.com/jj.0)