# Auto USBCamera detect
import subprocess
import re

def detect_cameras():
    result = subprocess.run(
        ["v4l2-ctl", "--list-devices"],
        capture_output=True,
        text=True
    )

    cameras = {}
    cam_id = 0
    blocks = result.stdout.split("\n\n")

    for block in blocks:
        if "usb-" not in block.lower():
            continue

        lines = block.strip().splitlines()
        name = lines[0].rstrip(":")

        for line in lines[1:]:
            match = re.search(r"/dev/video(\d+)", line)
            if match:
                index = int(match.group(1))
                cameras[cam_id] = {
                    "name": name,
                    "index": index
                }
                cam_id += 1
                break

    return cameras