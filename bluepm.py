import os
import subprocess
import argparse
import shutil

REPO_URL = "https://github.com/minhmc2007/Blue-Archive-Linux-Repo"
REPO_DIR = "Blue-Archive-Linux-Repo"
INSTALL_DIR = "/usr/bin"

# ANSI color codes for output
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def get_shell_rc_path():
    """Get the correct .zshrc path for the original user, even when run with sudo."""
    if os.environ.get("SUDO_USER"):
        user_home = os.path.expanduser(f"~{os.environ['SUDO_USER']}")
    else:
        user_home = os.path.expanduser("~")
    return os.path.join(user_home, ".zshrc")

def update_repo():
    """Update the package repository."""
    if not os.path.exists(REPO_DIR):
        subprocess.run(["git", "clone", REPO_URL], check=True)
    else:
        subprocess.run(["git", "-C", REPO_DIR, "pull"], check=True)
    print(f"{GREEN}Repository updated.{RESET}")

def install_package(package_name, method="copy"):
    """Install a package via copy or alias."""
    package_file = os.path.join(REPO_DIR, package_name)
    install_path = os.path.join(INSTALL_DIR, package_name)

    if not os.path.exists(package_file):
        print(f"{RED}❌ Error: Package '{package_name}' not found in the repository.{RESET}")
        return

    if method == "alias":
        print(f"{YELLOW}⚠ WARNING: --alias is a test feature under development and may not work correctly. Use at your own risk. ⚠{RESET}")
        shell_rc_path = get_shell_rc_path()
        with open(shell_rc_path, "a") as shellrc:
            shellrc.write(f"\nalias {package_name}='{package_file}'\n")
        print(f"{GREEN}✅ Alias '{package_name}' added. Run `source {shell_rc_path}` to apply changes.{RESET}")
    else:  # Default: copy method
        shutil.copy2(package_file, install_path)
        os.chmod(install_path, 0o755)
        print(f"{GREEN}✅ '{package_name}' installed and made executable.{RESET}")

def remove_package(package_name):
    """Remove a package (both copy and alias versions)."""
    executable = os.path.join(INSTALL_DIR, package_name)
    shell_rc_path = get_shell_rc_path()
    alias_removed = False

    # Remove alias from .zshrc
    if os.path.exists(shell_rc_path):
        with open(shell_rc_path, "r") as shellrc:
            lines = shellrc.readlines()
        with open(shell_rc_path, "w") as shellrc:
            for line in lines:
                if not line.strip().startswith(f"alias {package_name}="):
                    shellrc.write(line)
                else:
                    alias_removed = True

    if alias_removed:
        print(f"{GREEN}✅ Alias '{package_name}' removed. Run `source {shell_rc_path}` to apply changes.{RESET}")

    # Remove copied file
    if os.path.exists(executable):
        os.remove(executable)
        print(f"{GREEN}✅ '{package_name}' removed from {INSTALL_DIR}.{RESET}")
    else:
        print(f"{YELLOW}⚠ '{package_name}' not found in {INSTALL_DIR}.{RESET}")

def main():
    parser = argparse.ArgumentParser(description="BluePM - Blue Archive Linux Package Manager")
    parser.add_argument("--install", help="Install a package", metavar="PACKAGE")
    parser.add_argument("--alias", action="store_true", help="Use alias instead of copying (test feature)")
    parser.add_argument("--remove", help="Remove a package", metavar="PACKAGE")
    args = parser.parse_args()

    # Check for root privileges if the operation requires it
    if (args.install and not args.alias) or args.remove:
        if os.geteuid() != 0:
            print(f"{RED}❌ This operation requires root privileges. Please run the script with sudo.{RESET}")
            exit(1)

    if args.install:
        update_repo()
        install_package(args.install, method="alias" if args.alias else "copy")
    elif args.remove:
        remove_package(args.remove)

if __name__ == "__main__":
    main()
