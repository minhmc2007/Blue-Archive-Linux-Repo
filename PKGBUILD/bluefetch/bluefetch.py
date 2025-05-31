#!/usr/bin/env python3

import os
import platform
import subprocess
import shutil
import re

# Define the image path
IMAGE_PATH = "/blue-archive-fs/extra/arona.png"

def get_system_info():
    info = {}
    info['user'] = f"{os.getenv('USER')}@{platform.node()}"
    info['os'] = "Blue Archive Linux"
    info['kernel'] = subprocess.getoutput("uname -r")
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
        uptime_days = int(uptime_seconds / 86400)
        uptime_hours = int((uptime_seconds % 86400) / 3600)
        uptime_minutes = int((uptime_seconds % 3600) / 60)
        uptime_str = ""
        if uptime_days > 0:
            uptime_str += f"{uptime_days}d "
        uptime_str += f"{uptime_hours}h {uptime_minutes}m"
        info['uptime'] = uptime_str
    except:
        info['uptime'] = "Unknown"
    try:
        if shutil.which("pacman"):
            packages = subprocess.getoutput("pacman -Qq | wc -l")
            info['packages'] = f"{packages} (pacman)"
        else:
            info['packages'] = "Unknown"
    except:
        info['packages'] = "Unknown"
    info['shell'] = os.environ.get('SHELL', 'Unknown').split('/')[-1]
    info['de'] = os.environ.get('XDG_CURRENT_DESKTOP', 'Unknown')
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpu_info = f.read()
        cpu_model = re.search(r'model name\s*:\s*(.*)', cpu_info)
        info['cpu'] = cpu_model.group(1) if cpu_model else "Unknown"
    except:
        info['cpu'] = "Unknown"
    try:
        with open('/proc/meminfo', 'r') as f:
            mem_info = f.read()
        total_mem = re.search(r'MemTotal:\s*(\d+)', mem_info)
        available_mem = re.search(r'MemAvailable:\s*(\d+)', mem_info)
        if total_mem and available_mem:
            total = int(total_mem.group(1)) // 1024
            used = total - (int(available_mem.group(1)) // 1024)
            info['memory'] = f"{used}MiB / {total}MiB"
        else:
            info['memory'] = "Unknown"
    except:
        info['memory'] = "Unknown"
    return info

def display_image():
    w3mimgdisplay_path = "/usr/lib/w3m/w3mimgdisplay"
    if not os.path.exists(w3mimgdisplay_path):
        print("Error: w3mimgdisplay not found at /usr/lib/w3m/w3mimgdisplay.")
        return
    if os.path.exists(IMAGE_PATH):
        subprocess.run([w3mimgdisplay_path], input=f"0;1;0;0;300;300;{IMAGE_PATH}\n", text=True)
    else:
        print("Error: Arona image not found.")

def print_system_info():
    info = get_system_info()
    display_image()
    print(f"\n{{info['user']}}")
    print("=" * len(info['user']))
    print(f"OS: {{info['os']}}")
    print(f"Kernel: {{info['kernel']}}")
    print(f"Uptime: {{info['uptime']}}")
    print(f"Packages: {{info['packages']}}")
    print(f"Shell: {{info['shell']}}")
    print(f"DE: {{info['de']}}")
    print(f"CPU: {{info['cpu']}}")
    print(f"Memory: {{info['memory']}}\n")

if __name__ == "__main__":
    print_system_info()
