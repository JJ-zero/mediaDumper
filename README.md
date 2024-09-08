# MediaDumper
Simple tool to copy data from any connected media device into a local folder.

## Is this for me?
Probably not, to be honest, but if you have linux PC or server and often need to copy data from various media devices
(like SD cards or USB drives), this tool might be useful for you. I'm making this mainly for fast dumping of videos
from my drones, but if you are cinematographer or photographer, you might find this useful too.

## How to use it?
1. Clone or download this repository
0. Check if `lsblk` command is available on your system. If not, install it.
0. Check if `pmount` command is available on your system (probably not). If not, install it.
0. Create your config file. You can start by coping `config_template.json` to `config.json` and editing it.
    - `ignored` is a list of drives that are fully ignored by the script when looking for media devices.
    - `processes` is a list of definitions of processes that can be runned over found media drives. The key of an entry
    is used as a name of the process. You can choose what ever you want.
        - `script` is only required field in the process definition. It's the name of process class to be runned.
        - For other fields, check the documentation of the process class you want to use.
0. Create confing on you media device as `dump.json`. You can start by coping `dump_template.json` to `dump.json` and
editing it.
    - `process` - name of the process to be runned on this media device. It must be defined in `config.json`.
    - `checkpount` - Any kind on structure that selected process uses to store information about already processed files.
    - For other fields, check the documentation of the process class you want to use.
0. Run the script with `python3 main.py`. There is not really any support for having it as a service. Hopefully I will
get to it later.

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
- `self_checkpoint_reset` - Attept to detect if the media device was cleaned and reset the checkpoint if so.


## Do you want to help?
This is my personal project and I spend my personal time on it. That means I may not have time to implement everything.
If you are missing some feature or found a bug, feel free to create an issue or even a pull request.
If you are happy with the project and want to support it, you can buy me a tea. Otherwise, just
let me know that you like and / or use it. It's good motivation to keep going.


[![Buy me a coffee](https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20tea&emoji=🍵&slug=jj.0&button_colour=FFDD00&font_colour=000000&font_family=Arial&outline_colour=000000&coffee_colour=ffffff)](https://buymeacoffee.com/jj.0)