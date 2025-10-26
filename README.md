An incredibly barebones webui for managing a nonraid array. I want this to be a single tool that can be run to format disks, create an array, manage the array, setup mergerfs and mount a merged filesystem at /mnt/user like unraid does.

You can get it running with: `sudo python3 nmdctl-api.py` after installing nonraid and creating an array https://github.com/qvr/nonraid.

Todo:
Split the api/webui completely
Create api for smartctl
Allow formatting of disks from webui
Create an array from webui
Mergerfs setup from webui
