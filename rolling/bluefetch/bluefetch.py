#!/usr/bin/env python3

import os
import platform
import subprocess
import shutil
import re
import argparse

# Define the image path
IMAGE_PATH = "/blue-archive-fs/extra/arona.png"

def get_system_info():
    """Retrieve system information for display."""
    info = {}

    # Get user and hostname
    info['user'] = f"{os.getenv('USER')}@{platform.node()}"

    # Get OS info
    info['os'] = "Blue Archive Linux"

    # Get kernel version
    info['kernel'] = subprocess.getoutput("uname -r")

    # Get uptime
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

    # Get package count
    try:
        if shutil.which("pacman"):
            packages = subprocess.getoutput("pacman -Qq | wc -l")
            info['packages'] = f"{packages} (pacman)"
        else:
            info['packages'] = "Unknown"
    except:
        info['packages'] = "Unknown"

    # Get shell
    info['shell'] = os.environ.get('SHELL', 'Unknown').split('/')[-1]

    # Get desktop environment
    info['de'] = os.environ.get('XDG_CURRENT_DESKTOP', 'Unknown')

    # Get CPU info
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpu_info = f.read()
        cpu_model = re.search(r'model name\s*:\s*(.*)', cpu_info)
        info['cpu'] = cpu_model.group(1) if cpu_model else "Unknown"
    except:
        info['cpu'] = "Unknown"

    # Get memory info
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

def display_image(backend="catimg"):
    """Display the Arona image using the specified backend (catimg or w3m)."""
    if backend == "catimg":
        catimg_path = shutil.which("catimg")
        if not catimg_path:
            print("Error: catimg not found. Please install it or use --w3m.")
            return
        if os.path.exists(IMAGE_PATH):
            subprocess.run([catimg_path, IMAGE_PATH])
        else:
            print("Error: Arona image not found.")
    elif backend == "w3m":
        w3mimgdisplay_path = "/usr/lib/w3m/w3mimgdisplay"
        if not os.path.exists(w3mimgdisplay_path):
            print("Error: w3mimgdisplay not found at /usr/lib/w3m/w3mimgdisplay.")
            return
        if os.path.exists(IMAGE_PATH):
            subprocess.run([w3mimgdisplay_path], input=f"0;1;0;0;300;300;{IMAGE_PATH}\n", text=True)
        else:
            print("Error: Arona image not found.")

def print_system_info(backend="catimg"):
    """Print system information along with the image."""
    info = get_system_info()

    # Display the image using the chosen backend
    display_image(backend)

    # Print system information
    print(f"\n{info['user']}")
    print("=" * len(info['user']))
    print(f"OS: {info['os']}")
    print(f"Kernel: {info['kernel']}")
    print(f"Uptime: {info['uptime']}")
    print(f"Packages: {info['packages']}")
    print(f"Shell: {info['shell']}")
    print(f"DE: {info['de']}")
    print(f"CPU: {info['cpu']}")
    print(f"Memory: {info['memory']}\n")

def main():
    """Parse command-line arguments and run the script."""
    parser = argparse.ArgumentParser(description="A neofetch-like system info tool with Arona image.")
    parser.add_argument("--catimg", action="store_true", help="Use catimg to display the image (default)")
    parser.add_argument("--w3m", action="store_true", help="Use w3m to display the image")
    
    args = parser.parse_args()

    # Default to catimg unless w3m is explicitly specified
    if args.w3m and not args.catimg:
        backend = "w3m"
    else:
        backend = "catimg"

    print_system_info(backend)

if __name__ == "__main__":
    main()