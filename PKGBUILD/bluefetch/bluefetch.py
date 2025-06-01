
#!/usr/bin/env python3

import os
import platform
import subprocess
import shutil
import re
import sys
# import time # Optional

# --- Configuration ---
COLUMN_PADDING = "  " # Spaces between logo column and info column

# --- ANSI Colors ---
class Colors:
    RESET = "\033[0m"; BOLD = "\033[1m"; DIM = "\033[2m"
    BLACK = "\033[30m"; RED = "\033[31m"; GREEN = "\033[32m"; YELLOW = "\033[33m"
    BLUE = "\033[34m"; MAGENTA = "\033[35m"; CYAN = "\033[36m"; LIGHT_GRAY = "\033[37m"
    DARK_GRAY = "\033[90m"; LIGHT_RED = "\033[91m"; LIGHT_GREEN = "\033[92m"; LIGHT_YELLOW = "\033[93m"
    LIGHT_BLUE = "\033[94m"; LIGHT_MAGENTA = "\033[95m"; LIGHT_CYAN = "\033[96m"; WHITE = "\033[97m"

# --- Thematic Colors ---
THEME = {
    "title": Colors.BOLD + Colors.LIGHT_BLUE,
    "label": Colors.BOLD + Colors.CYAN,
    "value": Colors.WHITE,
    "error": Colors.BOLD + Colors.RED,
    "separator": Colors.DARK_GRAY,
    "logo_bleu": Colors.LIGHT_BLUE,
    "logo_arrhie": Colors.WHITE,
    "logo_linu": Colors.LIGHT_CYAN,
}

def get_terminal_size():
    try: return shutil.get_terminal_size()
    except Exception: return (80, 24)

def get_visible_length(s):
    return len(re.sub(r'\x1B\[[0-9;]*[mK]', '', s))

def get_system_info_lines():
    raw_info = get_system_info_data()
    info_lines_colored = []
    if raw_info.get('User'):
        user_line = f"{THEME['title']}{raw_info['User']}{Colors.RESET}"
        info_lines_colored.append(user_line)
        info_lines_colored.append(f"{THEME['title']}{'━' * get_visible_length(user_line)}{Colors.RESET}")
    key_order = ['OS', 'Kernel', 'Uptime', 'Packages', 'Shell', 'DE/WM', 'CPU', 'Memory']
    max_info_label_len = 0
    temp_info_kv = []
    for key in key_order:
        if key in raw_info:
            label_text = key
            max_info_label_len = max(max_info_label_len, len(label_text))
            temp_info_kv.append({'label_text': label_text, 'value_text': raw_info[key]})
    for item in temp_info_kv:
        label_colored = f"{THEME['label']}{item['label_text']}{Colors.RESET}"
        value_colored = f"{THEME['value']}{item['value_text']}{Colors.RESET}"
        padding = " " * (max_info_label_len - len(item['label_text']))
        info_lines_colored.append(f"{label_colored}{padding} {THEME['separator']}:{Colors.RESET} {value_colored}")
    return info_lines_colored

def get_system_info_data():
    info = {}
    info['User'] = f"{os.getenv('USER')}@{platform.node()}"
    info['OS'] = "Blue Archive Linux"
    info['Kernel'] = subprocess.getoutput("uname -r").strip()
    try:
        with open('/proc/uptime', 'r') as f: uptime_seconds = float(f.readline().split()[0])
        days=int(uptime_seconds/86400); hours=int((uptime_seconds%86400)/3600); minutes=int((uptime_seconds%3600)/60)
        u=[];
        if days > 0: u.append(f"{days}d")
        if hours > 0: u.append(f"{hours}h")
        if minutes > 0 or not u: u.append(f"{minutes}m")
        info['Uptime'] = " ".join(u) if u else "0m"
    except: info['Uptime'] = "N/A"
    try:
        if shutil.which("pacman"): info['Packages'] = f"{subprocess.getoutput('pacman -Qq --color never | wc -l').strip()} (pacman)"
        elif shutil.which("dpkg"): info['Packages'] = f"{subprocess.getoutput('dpkg-query -f \'.\n\' -W | wc -l').strip()} (dpkg)"
        elif shutil.which("rpm"): info['Packages'] = f"{subprocess.getoutput('rpm -qa | wc -l').strip()} (rpm)"
        else: info['Packages'] = "N/A"
    except: info['Packages'] = "N/A"
    info['Shell'] = os.path.basename(os.environ.get('SHELL', 'N/A'))
    de_wm = os.environ.get('XDG_CURRENT_DESKTOP',None) or os.environ.get('DESKTOP_SESSION',None) or "N/A"
    if de_wm!="N/A": de_wm = de_wm.split(':')[-1].replace('_',' ').title()
    info['DE/WM'] = de_wm
    try:
        with open('/proc/cpuinfo','r') as f: c = f.read()
        m = re.search(r'model name\s*:\s*(.*)',c)
        if m: info['CPU'] = ' '.join(re.sub(r'\s*CPU @ .*GHz|\((TM|tm|R|r)\)','',m.group(1).strip()).split())
        else: info['CPU'] = "N/A"
    except: info['CPU'] = "N/A"
    try:
        with open('/proc/meminfo','r') as f: mc = f.read()
        tm = re.search(r'MemTotal:\s*(\d+)\s*kB',mc); am = re.search(r'MemAvailable:\s*(\d+)\s*kB',mc)
        if tm and am: info['Memory'] = f"{(int(tm.group(1))-int(am.group(1)))//1024}MiB / {int(tm.group(1))//1024}MiB"
        else:
            fm=re.search(r'MemFree:\s*(\d+)\s*kB',mc); bm=re.search(r'Buffers:\s*(\d+)\s*kB',mc); cm=re.search(r'Cached:\s*(\d+)\s*kB',mc)
            if tm and fm and bm and cm: info['Memory'] = f"{(int(tm.group(1))-(int(fm.group(1))+int(bm.group(1))+int(cm.group(1))))//1024}MiB / {int(tm.group(1))//1024}MiB"
            else: info['Memory'] = "N/A"
    except: info['Memory'] = "N/A"
    return info

def get_manual_logo_lines():
    """Returns Blue Archive Linux ASCII art logo."""
    R = Colors.RESET
    C_BLUE = THEME['logo_bleu']
    C_ARCHIVE = THEME['logo_arrhie']
    C_LINUX = THEME['logo_linu']

    logo_lines = [
        # BLUE
        f"{C_BLUE}██████╗ ██╗     ██╗   ██╗███████╗{R}",
        f"{C_BLUE}██╔══██╗██║     ██║   ██║██╔════╝{R}",
        f"{C_BLUE}██████╔╝██║     ██║   ██║█████╗  {R}",
        f"{C_BLUE}██╔══██╗██║     ██║   ██║██╔══╝  {R}",
        f"{C_BLUE}██████╔╝███████╗╚██████╔╝███████╗{R}",
        f"{C_BLUE}╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝{R}",
        f"",
        # ARCHIVE
        f"{C_ARCHIVE} █████╗ ██████╗  ██████╗██╗  ██╗██╗██╗   ██╗███████╗{R}",
        f"{C_ARCHIVE}██╔══██╗██╔══██╗██╔════╝██║  ██║██║██║   ██║██╔════╝{R}",
        f"{C_ARCHIVE}███████║██████╔╝██║     ███████║██║██║   ██║█████╗  {R}",
        f"{C_ARCHIVE}██╔══██║██╔══██╗██║     ██╔══██║██║╚██╗ ██╔╝██╔══╝  {R}",
        f"{C_ARCHIVE}██║  ██║██║  ██║╚██████╗██║  ██║██║ ╚████╔╝ ███████╗{R}",
        f"{C_ARCHIVE}╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝  ╚══════╝{R}",
        f"",
        # LINUX
        f"{C_LINUX}██╗     ██╗███╗   ██╗██╗   ██╗██╗  ██╗{R}",
        f"{C_LINUX}██║     ██║████╗  ██║██║   ██║╚██╗██╔╝{R}",
        f"{C_LINUX}██║     ██║██╔██╗ ██║██║   ██║ ╚███╔╝ {R}",
        f"{C_LINUX}██║     ██║██║╚██╗██║██║   ██║ ██╔██╗ {R}",
        f"{C_LINUX}███████╗██║██║ ╚████║╚██████╔╝██╔╝ ██╗{R}",
        f"{C_LINUX}╚══════╝╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝{R}",
    ]
    
    return [line.rstrip() for line in logo_lines]

def print_layout():
    logo_lines_colored = get_manual_logo_lines()
    max_logo_width_chars = 0
    for line in logo_lines_colored:
        max_logo_width_chars = max(max_logo_width_chars, get_visible_length(line))

    info_lines_colored = get_system_info_lines()
    left_column_width_chars = max_logo_width_chars
    num_logo_lines = len(logo_lines_colored)
    num_info_lines = len(info_lines_colored)
    total_max_lines = max(num_logo_lines, num_info_lines)

    print()
    for i in range(total_max_lines):
        left_part = logo_lines_colored[i] if i < num_logo_lines else ""
        right_part = info_lines_colored[i] if i < num_info_lines else ""
        current_left_width = get_visible_length(left_part)
        padding_spaces = left_column_width_chars - current_left_width
        padded_left_part = left_part + " " * max(0, padding_spaces)
        line_to_print = f"{padded_left_part}{COLUMN_PADDING}{right_part}"
        print(line_to_print)
    print_color_palette_standalone()

def print_color_palette_standalone():
    blocks = "████"; output_line = ""
    for i in range(8): output_line += f"\033[4{i}m{blocks}{Colors.RESET}"
    output_line += "  "
    for i in range(8): output_line += f"\033[10{i}m{blocks}{Colors.RESET}"
    print(f"\n{output_line}")

if __name__ == "__main__":
    print_layout()
