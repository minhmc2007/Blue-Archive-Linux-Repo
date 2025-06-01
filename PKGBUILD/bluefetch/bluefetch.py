#!/usr/bin/env python3

import os
import platform
import subprocess
import shutil
import re
import sys
# import time # Not strictly needed anymore for the delay

# --- Configuration ---
IMAGE_PATH = "/blue-archive-fs/extra/arona.png"  # YOUR Arona image path
DEFAULT_IMAGE_WIDTH_PERCENT = 0.3  # Image width as a percentage of terminal width (approx)
MIN_IMAGE_WIDTH_PX = 50
MAX_IMAGE_WIDTH_PX = 350 # Max width of image in pixels
MIN_IMAGE_HEIGHT_PX = 50
MAX_IMAGE_HEIGHT_PX = 280 # Max height of image in pixels
IMAGE_ASPECT_RATIO = 1.0  # Width / Height. Adjust if your image isn't square.

# w3mimgdisplay draw coordinates & text estimation
IMG_DRAW_X_PX = 5  # Top-left X for image (pixels)
IMG_DRAW_Y_PX = 5  # Top-left Y for image (pixels)
CHAR_HEIGHT_APPROX_PX = 16 # Estimated pixel height of a terminal character row
CHAR_WIDTH_APPROX_PX = 8   # Estimated pixel width of a terminal character
TEXT_PADDING_CHARS_AFTER_IMAGE = 3 # Extra character spaces between image and text

# --- ANSI Colors ---
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    # ... (other colors as defined before)
    BLACK = "\033[30m"; RED = "\033[31m"; GREEN = "\033[32m"; YELLOW = "\033[33m"
    BLUE = "\033[34m"; MAGENTA = "\033[35m"; CYAN = "\033[36m"; LIGHT_GRAY = "\033[37m"
    DARK_GRAY = "\033[90m"; LIGHT_RED = "\033[91m"; LIGHT_GREEN = "\033[92m"; LIGHT_YELLOW = "\033[93m"
    LIGHT_BLUE = "\033[94m"; LIGHT_MAGENTA = "\033[95m"; LIGHT_CYAN = "\033[96m"; WHITE = "\033[97m"
    BG_BLACK = "\033[40m"; BG_RED = "\033[41m"; BG_GREEN = "\033[42m"; BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"; BG_MAGENTA = "\033[45m"; BG_CYAN = "\033[46m"; BG_LIGHT_GRAY = "\033[47m"
    BG_DARK_GRAY = "\033[100m"

# --- Thematic Colors ---
THEME = {
    "title": Colors.BOLD + Colors.LIGHT_BLUE,
    "label": Colors.BOLD + Colors.CYAN,
    "value": Colors.WHITE,
    "error": Colors.BOLD + Colors.RED,
    "separator": Colors.DARK_GRAY,
    "logo_main": Colors.LIGHT_BLUE,
    "logo_accent": Colors.WHITE,
}

def get_terminal_size():
    try:
        return shutil.get_terminal_size()
    except Exception:
        return (80, 24)

def cprint(text, color_key=None, end="\n", file=sys.stdout):
    color_code = THEME.get(color_key, "")
    print(f"{color_code}{text}{Colors.RESET}", end=end, file=file)

def get_system_info():
    info = {}
    info['User'] = f"{os.getenv('USER')}@{platform.node()}"
    info['OS'] = "Blue Archive Linux"
    info['Kernel'] = subprocess.getoutput("uname -r").strip()

    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
        days = int(uptime_seconds / 86400)
        hours = int((uptime_seconds % 86400) / 3600)
        minutes = int((uptime_seconds % 3600) / 60)
        uptime_str_parts = []
        if days > 0: uptime_str_parts.append(f"{days}d")
        if hours > 0: uptime_str_parts.append(f"{hours}h")
        if minutes > 0 or not uptime_str_parts: uptime_str_parts.append(f"{minutes}m")
        info['Uptime'] = " ".join(uptime_str_parts) if uptime_str_parts else "0m"
    except Exception:
        info['Uptime'] = "N/A"

    try:
        if shutil.which("pacman"):
            packages = subprocess.getoutput("pacman -Qq --color never | wc -l").strip()
            info['Packages'] = f"{packages} (pacman)"
        elif shutil.which("dpkg"):
            packages = subprocess.getoutput("dpkg-query -f '.\n' -W | wc -l").strip()
            info['Packages'] = f"{packages} (dpkg)"
        elif shutil.which("rpm"):
            packages = subprocess.getoutput("rpm -qa | wc -l").strip()
            info['Packages'] = f"{packages} (rpm)"
        else:
            info['Packages'] = "N/A"
    except Exception:
        info['Packages'] = "N/A"

    info['Shell'] = os.path.basename(os.environ.get('SHELL', 'N/A'))
    de_wm = os.environ.get('XDG_CURRENT_DESKTOP', None) or \
            os.environ.get('DESKTOP_SESSION', None) or "N/A"
    if de_wm != "N/A":
        de_wm = de_wm.split(':')[-1].replace('_', ' ').title()
    info['DE/WM'] = de_wm

    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpu_info_content = f.read()
        cpu_model_match = re.search(r'model name\s*:\s*(.*)', cpu_info_content)
        if cpu_model_match:
            cpu_model = cpu_model_match.group(1).strip()
            cpu_model = re.sub(r'\s*CPU @ .*GHz', '', cpu_model) # Optional: Shorten
            cpu_model = re.sub(r'\((TM|tm|R|r)\)', '', cpu_model) # Remove (TM), (R)
            cpu_model = ' '.join(cpu_model.split())
            info['CPU'] = cpu_model
        else:
            info['CPU'] = "N/A"
    except Exception:
        info['CPU'] = "N/A"

    try:
        with open('/proc/meminfo', 'r') as f:
            mem_info_content = f.read()
        total_mem_match = re.search(r'MemTotal:\s*(\d+)\s*kB', mem_info_content)
        available_mem_match = re.search(r'MemAvailable:\s*(\d+)\s*kB', mem_info_content)

        if total_mem_match and available_mem_match:
            total_kb = int(total_mem_match.group(1))
            available_kb = int(available_mem_match.group(1))
            used_kb = total_kb - available_kb
            info['Memory'] = f"{used_kb // 1024}MiB / {total_kb // 1024}MiB"
        else: # Fallback if MemAvailable is not present (older kernels)
            free_mem_match = re.search(r'MemFree:\s*(\d+)\s*kB', mem_info_content)
            buffers_match = re.search(r'Buffers:\s*(\d+)\s*kB', mem_info_content)
            cached_match = re.search(r'Cached:\s*(\d+)\s*kB', mem_info_content) # Simple cached
            sreclaim_match = re.search(r'SReclaimable:\s*(\d+)\s*kB', mem_info_content)

            if total_mem_match and free_mem_match and buffers_match and cached_match:
                total_kb = int(total_mem_match.group(1))
                free_kb = int(free_mem_match.group(1))
                buffers_kb = int(buffers_match.group(1))
                # More accurate "used" calculation for older kernels:
                # Used = Total - Free - Buffers - Cached (where Cached includes SReclaimable)
                # Or, if SReclaimable is available, Used = Total - (Free + Buffers + SReclaimable)
                cached_kb = int(cached_match.group(1))
                sreclaim_kb = int(sreclaim_match.group(1)) if sreclaim_match else 0

                if sreclaim_kb > 0 : # SReclaimable is part of "Cached" but considered "available"
                     used_kb = total_kb - (free_kb + buffers_kb + sreclaim_kb)
                else: # Simpler fallback
                     used_kb = total_kb - (free_kb + buffers_kb + cached_kb)

                info['Memory'] = f"{used_kb // 1024}MiB / {total_kb // 1024}MiB"
            else:
                info['Memory'] = "N/A"
    except Exception:
        info['Memory'] = "N/A"
    return info

def display_image(image_path, terminal_width_chars, terminal_height_lines):
    """
    Attempts to display an image using w3mimgdisplay.
    Returns:
        (int): Estimated number of text lines the image area (y_offset + height) might cover.
        (int): Estimated width in pixels that the image area (x_offset + width) occupies from screen left.
               This is used to calculate text indentation.
    """
    w3mimgdisplay_path = shutil.which("w3mimgdisplay")
    if not w3mimgdisplay_path:
        cprint("w3mimgdisplay not found. Cannot display image.", "error", file=sys.stderr)
        return 0, 0

    if not os.path.exists(image_path):
        cprint(f"Image not found: {image_path}", "error", file=sys.stderr)
        return 0, 0

    # Calculate image dimensions
    term_width_px = terminal_width_chars * CHAR_WIDTH_APPROX_PX
    
    img_w = int(term_width_px * DEFAULT_IMAGE_WIDTH_PERCENT)
    img_w = max(MIN_IMAGE_WIDTH_PX, min(img_w, MAX_IMAGE_WIDTH_PX))
    
    img_h = int(img_w / IMAGE_ASPECT_RATIO)
    img_h = max(MIN_IMAGE_HEIGHT_PX, min(img_h, MAX_IMAGE_HEIGHT_PX))

    # Ensure image doesn't exceed terminal height (approx)
    max_allowable_h = (terminal_height_lines * CHAR_HEIGHT_APPROX_PX) - IMG_DRAW_Y_PX - 10 # -10 for safety margin
    if img_h > max_allowable_h:
        img_h = max_allowable_h
        img_w = int(img_h * IMAGE_ASPECT_RATIO) # Recalculate width based on new height

    if img_w <=0 or img_h <=0: # Safety check
        return 0,0

    try:
        # Flushing stdout is important before calling w3mimgdisplay if it uses stdin/out
        sys.stdout.flush()
        input_str = f"0;1;{IMG_DRAW_X_PX};{IMG_DRAW_Y_PX};{img_w};{img_h};;;;;{image_path}\n4;\n3;\n"
        process = subprocess.run(
            [w3mimgdisplay_path],
            input=input_str,
            text=True,
            timeout=2,
            stdout=subprocess.PIPE, # Capture stdout to get dimensions if needed, though not strictly used here
            stderr=subprocess.PIPE
        )
        if process.returncode != 0:
            # cprint(f"w3mimgdisplay error (ret {process.returncode}): {process.stderr.strip()}", "error", file=sys.stderr)
            # Silently fail on error for now, as errors can be spammy
            return 0,0

        lines_covered = (IMG_DRAW_Y_PX + img_h + CHAR_HEIGHT_APPROX_PX -1) // CHAR_HEIGHT_APPROX_PX # Round up
        width_occupied_px = IMG_DRAW_X_PX + img_w
        return lines_covered, width_occupied_px
    except subprocess.TimeoutExpired:
        cprint("w3mimgdisplay timed out.", "error", file=sys.stderr)
    except Exception as e:
        cprint(f"Failed to display image: {e}", "error", file=sys.stderr)
    return 0, 0

def print_color_palette(prefix=""):
    blocks = "████"
    output_line = ""
    for i in range(8): # Normal colors
        output_line += f"\033[4{i}m{blocks}{Colors.RESET}"
    output_line += "  " # Separator
    for i in range(8): # Bright colors
        output_line += f"\033[10{i}m{blocks}{Colors.RESET}"
    print(f"{prefix}{output_line}")

def print_system_info():
    terminal_cols, terminal_rows = get_terminal_size()

    # Attempt to display image and get its screen footprint
    # lines_image_covers_v: how many text lines down the image area extends
    # image_right_edge_px: pixel X-coordinate of the right edge of the image area
    lines_image_covers_v, image_right_edge_px = display_image(IMAGE_PATH, terminal_cols, terminal_rows)

    text_indent_str = ""
    if lines_image_covers_v > 0 and image_right_edge_px > 0:
        # Calculate how many characters to indent text that is "behind" the image
        indent_chars_count = (image_right_edge_px // CHAR_WIDTH_APPROX_PX) + TEXT_PADDING_CHARS_AFTER_IMAGE
        text_indent_str = " " * indent_chars_count

    current_line_num = 0  # Tracks the current line number we are about to print text on

    # --- Logo ---
    logo_art_lines = [
        f"{THEME['logo_main']}██████╗ {THEME['logo_accent']}   █████╗  ",
        f"{THEME['logo_main']}██╔══██╗{THEME['logo_accent']}  ██╔══██╗ ",
        f"{THEME['logo_main']}██████╔╝{THEME['logo_accent']}  ███████║ ",
        f"{THEME['logo_main']}██╔══██╗{THEME['logo_accent']}  ██╔══██║ ",
        f"{THEME['logo_main']}██████╔╝{THEME['logo_accent']}  ██╔══██║ ",
        f"{THEME['logo_main']}╚═════╝ {THEME['logo_accent']}  ╚═╝  ╚═╝ ",
        f"        {Colors.DIM}L I N U X{Colors.RESET}"
    ]
    for line_content in logo_art_lines:
        prefix = text_indent_str if current_line_num < lines_image_covers_v else ""
        print(f"{prefix}{line_content}{Colors.RESET}")
        current_line_num += 1
    
    # Blank line after logo
    prefix = text_indent_str if current_line_num < lines_image_covers_v else ""
    print(prefix)
    current_line_num += 1

    # --- System Info ---
    info = get_system_info()
    info_display_lines = [] # Store (prefix, line_content) tuples

    # User & Separator
    if info.get('User'):
        user_line = f"{THEME['title']}{info['User']}{Colors.RESET}"
        separator_line = f"{THEME['separator']}{'━' * len(info['User'])}{Colors.RESET}"
        info_display_lines.append(user_line)
        info_display_lines.append(separator_line)

    # Key-Value Pairs
    key_order = ['OS', 'Kernel', 'Uptime', 'Packages', 'Shell', 'DE/WM', 'CPU', 'Memory']
    kv_pairs_for_formatting = []
    max_label_len = 0
    for key in key_order:
        if key in info:
            label_colored = f"{THEME['label']}{key}{Colors.RESET}"
            value_colored = f"{THEME['value']}{info[key]}{Colors.RESET}"
            kv_pairs_for_formatting.append({'label': label_colored, 'value': value_colored})
            plain_label = re.sub(r'\033\[[0-9;]*m', '', label_colored) # For length calculation
            max_label_len = max(max_label_len, len(plain_label))

    for item in kv_pairs_for_formatting:
        plain_label = re.sub(r'\033\[[0-9;]*m', '', item['label'])
        padding = " " * (max_label_len - len(plain_label))
        info_line = f"{item['label']}{padding} {THEME['separator']}:{Colors.RESET} {item['value']}"
        info_display_lines.append(info_line)

    # Print all info lines with appropriate prefix
    for line_content in info_display_lines:
        prefix = text_indent_str if current_line_num < lines_image_covers_v else ""
        print(f"{prefix}{line_content}")
        current_line_num += 1
    
    # --- Color Palette ---
    # Blank line before palette
    prefix = text_indent_str if current_line_num < lines_image_covers_v else ""
    print(prefix)
    current_line_num += 1

    # Palette line itself
    palette_prefix = text_indent_str if current_line_num < lines_image_covers_v else ""
    print_color_palette(prefix=palette_prefix)
    current_line_num +=1

    # Final blank line for spacing
    prefix = text_indent_str if current_line_num < lines_image_covers_v else ""
    print(prefix)
    # current_line_num += 1 # Not strictly needed after the last print

if __name__ == "__main__":
    # Optional: Clear screen if you prefer a fresh display
    # print("\033c", end="") # Clears screen and scrollback for some terminals
    # print("\033[H\033[2J", end="") # POSIX clear screen

    print_system_info()

    # A small delay was sometimes used to ensure w3mimgdisplay finishes drawing
    # before the script exits and the terminal potentially closes or redraws.
    # Modern terminals handle this better, but if you see flicker, uncomment:
    # time.sleep(0.05)
