#!/usr/bin/env python3
"""
default.json Configuration Updater
Version: 10.2.0.0
Purpose: Ensures default.json contains the incognito mode setting
"""

import os
import json
import sys
from termcolor import colored  # Consistent with main script

# Constants
CONFIG_PATH = "/data/data/com.termux/files/home/default.json"
INCOGNITO_KEY = "incognito"
DEFAULT_VALUE = "off"
BACKUP_KEY = "history_backup"

def update_config():
    """Main function to update the configuration file"""
    if not os.path.isfile(CONFIG_PATH):
        print(colored("Config file not found, skipping update.", "yellow"))
        return False

    try:
        with open(CONFIG_PATH, 'r+', encoding='utf-8') as f:
            try:
                config = json.load(f)
            except json.JSONDecodeError:
                print(colored("Error: Invalid JSON format in config file.", "red"))
                return False

            # Check if incognito key exists in default section
            if "default" in config and isinstance(config["default"], list):
                if len(config["default"]) > 0:
                    default_section = config["default"][0]
                    if INCOGNITO_KEY not in default_section:
                        # Add incognito key with default value
                        default_section[INCOGNITO_KEY] = DEFAULT_VALUE
                        print(colored("Added incognito mode setting to config.", "green"))
                        
                        # Remove backup key if it exists
                        if BACKUP_KEY in default_section:
                            del default_section[BACKUP_KEY]
                        
                        # Write changes back to file
                        f.seek(0)
                        json.dump(config, f, indent=4)
                        f.truncate()
                        return True
                else:
                    print(colored("Error: Empty default section in config.", "red"))
            else:
                print(colored("Error: Invalid config structure - missing default section.", "red"))
    
    except IOError as e:
        print(colored(f"Error accessing config file: {str(e)}", "red"))
    
    return False

def main():
    print(colored("\nConfig File Updater", "blue"))
    print(colored("Checking configuration...\n", "cyan"))
    
    if update_config():
        print(colored("\nConfiguration updated successfully!", "green"))
    else:
        print(colored("\nNo updates needed.", "yellow"))
    
    # Self-cleanup
    try:
        os.remove(sys.argv[0])
        print(colored("Cleanup complete.", "green"))
    except OSError as e:
        print(colored(f"Error during cleanup: {str(e)}", "red"))

if __name__ == "__main__":
    main()
