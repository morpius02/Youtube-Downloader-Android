#!/data/data/com.termux/files/usr/bin/env python3
"""
Termux Downloader Updater
Version: 10.2.0.0
Purpose: Handles version checking and updates for Termux Downloader
"""

import os
import sys
import json
import re
import time
import requests
from datetime import date, datetime
from termcolor import colored, cprint
from bs4 import BeautifulSoup

# Constants
HOME_DIR = "/data/data/com.termux/files/home"
MAIN_SCRIPT = f"{HOME_DIR}/main.py"
CONFIG_FILE = f"{HOME_DIR}/default.json"
TEMP_FILE = f"{HOME_DIR}/noobjection.temp"
REFRESH_SCRIPT = f"{HOME_DIR}/refresh.sh"
GITHUB_URL = "https://raw.githubusercontent.com/DrDelin/Youtube-Downloader-Android/master/YTD_Android.py"

# Patterns for version validation
VERSION_PATTERN = r"^#Version\s\d+\.\d+\.\d+\.\d+$"
ENGINE_PATTERN = r"^#Engine\s\d+\.\d+$"

def get_local_version():
    """Get local version and engine information"""
    try:
        with open(MAIN_SCRIPT, 'r') as f:
            lines = f.readlines()
            local_version = lines[0] if len(lines) > 0 else "#Version 0.0.0.0\n"
            local_engine = lines[1] if len(lines) > 1 else "#Engine 0.0\n"
        return local_version, local_engine
    except Exception as e:
        print(colored(f"Error reading local version: {str(e)}", 'red'))
        return "#Version 0.0.0.0\n", "#Engine 0.0\n"

def get_cloud_version():
    """Get cloud version information with robust error handling"""
    try:
        response = requests.get(GITHUB_URL, timeout=10)
        response.raise_for_status()
        content = response.text
        
        # Find version line
        version_line = next((line for line in content.split('\n') if line.startswith("#Version")), None)
        cloud_version = version_line + "\n" if version_line and re.match(VERSION_PATTERN, version_line) else None
        
        # Find engine line
        engine_line = next((line for line in content.split('\n') if line.startswith("#Engine")), None)
        cloud_engine = engine_line + "\n" if engine_line and re.match(ENGINE_PATTERN, engine_line) else None
        
        return cloud_version, cloud_engine, True
    except Exception as e:
        print(colored(f"Update server error: {str(e)}", 'yellow'))
        return None, None, False

def print_status(server_active, failsafe_active):
    """Print system status information"""
    status_items = [
        ("Update Server", 'green' if server_active else 'red'),
        ("Failsafe System", 'red' if failsafe_active else 'green'),
        ("Auto Upgrade", 'green'),
        ("Downloader", 'green')
    ]
    
    status_text = "\n".join([
        f"{colored(label+':', 'cyan')} {colored('ACTIVE' if color == 'green' else 'INACTIVE', color)}"
        for label, color in status_items
    ])
    
    cprint("\nSYSTEM STATUS", 'cyan', attrs=['bold'])
    print(status_text + "\n")

def check_upgrade_date():
    """Check if upgrade is needed based on last upgrade date"""
    try:
        today = date.today().strftime("%d/%m/%Y")
        
        if not os.path.exists(CONFIG_FILE):
            return False, "No config file found"
            
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            last_upgrade = config["default"][0].get("last_upgrade", "")
            
            if not last_upgrade:
                config["default"][0]["last_upgrade"] = today
                with open(CONFIG_FILE, 'w') as fw:
                    json.dump(config, fw, indent=4)
                return False, f"First run recorded: {today}"
            
            days_since = (datetime.strptime(today, "%d/%m/%Y") - 
                         datetime.strptime(last_upgrade, "%d/%m/%Y")).days
                         
            if days_since > 28:
                config["default"][0]["last_upgrade"] = today
                with open(CONFIG_FILE, 'w') as fw:
                    json.dump(config, fw, indent=4)
                return True, "Binaries outdated"
                
            return False, f"Last upgrade: {last_upgrade} ({days_since} days ago)"
            
    except Exception as e:
        return False, f"Error checking upgrade: {str(e)}"

def perform_upgrade(engine_update=False):
    """Perform the upgrade process"""
    try:
        # Create temp file to indicate upgrade mode
        open(TEMP_FILE, 'a').close()
        
        # Run refresh script
        upgrade_type = "engine" if engine_update else "normal"
        print(colored(f"\nPerforming {upgrade_type} upgrade...", 'yellow'))
        os.system(f"sh {REFRESH_SCRIPT} auto")
        
        # Cleanup
        if os.path.exists(TEMP_FILE):
            os.remove(TEMP_FILE)
            
        print(colored("\nUpgrade completed successfully!", 'green'))
        return True
    except Exception as e:
        print(colored(f"\nUpgrade failed: {str(e)}", 'red'))
        return False

def main():
    start_time = time.time()
    
    # Print welcome banner
    cprint("\nTERMUX DOWNLOADER UPDATER", 'cyan', 'on_red', attrs=['bold'])
    print(colored(f"Version: 10.2.0.0\n", 'yellow'))
    
    # Get version information
    local_version, local_engine = get_local_version()
    cloud_version, cloud_engine, server_active = get_cloud_version()
    
    # Use local versions if cloud fetch failed
    if not server_active:
        cloud_version = local_version
        cloud_engine = local_engine
    
    # Print system status
    print_status(server_active, not server_active)
    
    # Print ping time
    ping_time = (time.time() - start_time) * 1000
    print(f"[Ping: {ping_time:.02f}ms]\n")
    
    # Handle forced upgrade mode
    if len(sys.argv) > 1 and sys.argv[1] == "forced":
        print(colored("Running forced manual upgrade...", 'yellow'))
        perform_upgrade()
        return
    
    # Normal operation mode
    command = f'python "{MAIN_SCRIPT}" "{sys.argv[1]}"' if len(sys.argv) > 1 else ""
    
    # Check engine updates first
    if cloud_engine != local_engine:
        print(colored("\nNew Engine version available!", 'green'))
        print(f"Current: {local_engine.strip()}")
        print(f"Available: {cloud_engine.strip()}\n")
        
        # Update last upgrade date
        today = date.today().strftime("%d/%m/%Y")
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r+') as f:
                config = json.load(f)
                config["default"][0]["last_upgrade"] = today
                f.seek(0)
                json.dump(config, f, indent=4)
        
        # Perform upgrade
        if perform_upgrade(engine_update=True) and command:
            os.system(command)
        return
    
    # Check for regular updates
    needs_upgrade, upgrade_msg = check_upgrade_date()
    print(colored(f"\n{upgrade_msg}", 'blue'))
    
    if cloud_version != local_version:
        print(colored("\nNew version available!", 'green'))
        print(f"Current: {local_version.strip()}")
        print(f"Available: {cloud_version.strip()}\n")
        
        if perform_upgrade() and command:
            os.system(command)
    elif needs_upgrade:
        print(colored("\nPerforming routine binaries update...", 'yellow'))
        perform_upgrade()
        if command:
            os.system(command)
    else:
        print(colored("\nNo updates available.", 'green'))
        if command:
            os.system(command)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(colored("\nUpdate cancelled by user.", 'red'))
        sys.exit(1)
    except Exception as e:
        print(colored(f"\nCritical error: {str(e)}", 'red'))
        sys.exit(1)
