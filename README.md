# Caldera for OT plugin: Snap7
A Caldera for OT plugin providing Caldera with S7comm protocol support.


# Installation
This module relies on [Snap7 library](https://snap7.sourceforge.net/)

Install it according to the project's documentation

## Building the payload

```bash
pip install pyinstaller
pip install python-snap7
cd caldera-snap7/src/src
./create_payload.sh
```


## Enabling the plugin
To run Caldera along with snap7 plugin:

- Download Caldera as detailed in the Installation Guide
- Copy the snap7 plugin in Caldera's plugin directory: `caldera/plugins` and rename the folder it to ``snap7``
- Enable the snap7 plugin by adding `- snap7` to the list of enabled plugins in `conf/local.yml` or `conf/default.yml` (if running Caldera in insecure mode)
Version

# Description

abilities available in the snap7 plugin:
- Gathering data from PLC
- read Data Block
- write Data Block
- fuzz Data Block
- read/write other data types




