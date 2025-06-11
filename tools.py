#!/data/data/com.termux/files/usr/bin/env python3
import os
import json
import sys
from datetime import datetime, date
from pathlib import Path
import shutil
from termcolor import colored

# Version information
UTILS_VERSION = "10.2.0.0"
print("\n")
print(colored("TERMUX DOWNLOADER UTILITIES", 'red', attrs=['bold']))
print(colored(f"Version: {UTILS_VERSION}\n", 'yellow'))

# Constants
HOME_DIR = "/data/data/com.termux/files/home"
STORAGE_DIR = "/storage/emulated/0/Termux_Downloader"
HISTORY_FILE = f"{HOME_DIR}/history.txt"
CONFIG_FILE = f"{HOME_DIR}/default.json"
MAIN_SCRIPT = f"{HOME_DIR}/main.py"

def clear_screen():
    os.system('clear')

def print_header(title):
    clear_screen()
    print(colored(f"\n{title}", 'blue', attrs=['bold']))
    print(colored("=" * len(title) + "\n", 'blue'))

def import_history():
    """Import history from storage to Termux"""
    print_header("HISTORY IMPORT")
    
    # Check for history files in storage
    txt_files = list(Path(STORAGE_DIR).glob("*.txt"))
    if not txt_files:
        print(colored("No history files found in Termux_Downloader folder!", 'red'))
        return
    
    print(colored("Keep only one history text file in Termux_Downloader folder", 'yellow'))
    input(colored("Press Enter to continue...", 'grey'))
    
    if len(txt_files) > 1:
        print(colored("Multiple history files found. Please keep only one.", 'red'))
        return
    
    source_file = str(txt_files[0])
    
    # If no existing history, just move the file
    if not os.path.exists(HISTORY_FILE):
        shutil.move(source_file, HISTORY_FILE)
        print(colored("History imported successfully!", 'green'))
        return
    
    # Merge histories if both exist
    print(colored("Merging with existing history...", 'cyan'))
    
    with open(HISTORY_FILE, 'r') as f:
        existing_lines = len(f.readlines())
    
    new_entries = 0
    with open(source_file, 'r') as src, open(HISTORY_FILE, 'a') as dest:
        for line in src:
            try:
                entry = json.loads(line)
                entry["SNo"] = str(existing_lines + new_entries + 1)
                dest.write(json.dumps(entry) + "\n")
                new_entries += 1
            except json.JSONDecodeError:
                continue
    
    os.remove(source_file)
    print(colored(f"Successfully merged {new_entries} history entries!", 'green'))

def manual_download():
    """Manual download from entered URL"""
    print_header("MANUAL DOWNLOAD")
    link = input(colored("Enter the URL: \n", 'yellow'))
    if link:
        os.system(f'python "{MAIN_SCRIPT}" "{link}"')

def toggle_incognito():
    """Toggle incognito mode in config"""
    with open(CONFIG_FILE, 'r+') as f:
        config = json.load(f)
        current_state = config["default"][0]["incognito"]
        new_state = "off" if current_state == "on" else "on"
        config["default"][0]["incognito"] = new_state
        f.seek(0)
        json.dump(config, f, indent=4)
        f.truncate()
    
    print(colored(f"\nIncognito Mode Turned: {new_state.upper()}", 'green'))

def backup_history():
    """Backup history to storage"""
    print_header("HISTORY BACKUP")
    
    if not os.path.exists(HISTORY_FILE):
        print(colored("No history file available to backup!", 'red'))
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{STORAGE_DIR}/history_backup_{timestamp}.txt"
    
    shutil.copy2(HISTORY_FILE, backup_path)
    print(colored(f"History backup created at:\n{backup_path}", 'green'))

def delete_history():
    """Delete history file with confirmation"""
    print_header("DELETE HISTORY")
    
    if not os.path.exists(HISTORY_FILE):
        print(colored("No history file available to delete!", 'red'))
        return
    
    confirm = input(colored("Type 'YES' to confirm deletion: ", 'red'))
    if confirm == "YES":
        os.remove(HISTORY_FILE)
        print(colored("History file deleted!", 'green'))
    else:
        print(colored("Deletion cancelled.", 'yellow'))

def show_script_info():
    """Display script version and information"""
    print_header("SCRIPT INFORMATION")
    
    with open(MAIN_SCRIPT, 'r') as f:
        lines = [f.readline().strip() for _ in range(3)]
    
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
        last_upgrade = config["default"][0]["last_upgrade"]
        inc_state = config["default"][0]["incognito"].capitalize()
    
    today = date.today().strftime("%d/%m/%Y")
    days_left = 28 - (datetime.strptime(today, "%d/%m/%Y") - 
                     datetime.strptime(last_upgrade, "%d/%m/%Y")).days
    
    info = [
        ("Version", lines[0].replace("#Version ", "")),
        ("Engine", lines[1].replace("#Engine ", "")),
        ("Build", lines[2].replace("#", "")),
        ("Last Upgrade", last_upgrade),
        ("Auto-upgrade In", f"{days_left} days"),
        ("Incognito Mode", inc_state)
    ]
    
    for label, value in info:
        print(colored(f"{label:<15}", 'cyan') + colored(value, 'white'))

def show_dev_info():
    """Show developer information and links"""
    print_header("DEVELOPER INFORMATION")
    
    options = [
        ("1", "Official Termux GitHub", "https://github.com/termux/termux-app"),
        ("2", "Termux Releases", "https://github.com/termux/termux-app/releases"),
        ("3", "Script GitHub", "https://github.com/DrDelin/Youtube-Downloader-Android"),
        ("4", "Report Issues", "https://github.com/DrDelin/Youtube-Downloader-Android/issues")
    ]
    
    for num, desc, _ in options:
        print(colored(f"{num}. {desc}", 'yellow'))
    
    choice = input("\nChoose an option (or Enter to exit): ")
    for num, _, url in options:
        if choice == num:
            os.system(f"termux-open-url {url}")
            return

def main_menu():
    """Display main menu and handle choices"""
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
        inc_state = config["default"][0]["incognito"]
        toggle_text = "On" if inc_state == "off" else "Off"
    
    menu = [
        ("Tools", [
            ("1", "Manual Link Download")
        ]),
        ("History", [
            ("2", "View Download History"),
            ("3", f"Turn {toggle_text} Incognito Mode"),
            ("4", "Backup History"),
            ("5", "Import History"),
            ("6", "Delete History")
        ]),
        ("Troubleshooting", [
            ("7", "Manual Upgrade"),
            ("8", "Factory Reset")
        ]),
        ("Info", [
            ("9", "Script Build Info"),
            ("10", "Developer Info")
        ])
    ]
    
    clear_screen()
    print(colored("\nMAIN MENU\n", 'blue', attrs=['bold']))
    
    for section, items in menu:
        print(colored(section, 'green'))
        for num, desc in items:
            print(colored(f"  {num}. {desc}", 'yellow'))
        print()
    
    choice = input(colored("Enter your choice: ", 'cyan'))
    
    actions = {
        '1': manual_download,
        '2': lambda: os.system(f'python "{HOME_DIR}/history.py"'),
        '3': toggle_incognito,
        '4': backup_history,
        '5': import_history,
        '6': delete_history,
        '7': lambda: os.system("sh refresh.sh"),
        '8': lambda: os.system("sh refresh.sh"),
        '9': show_script_info,
        '10': show_dev_info
    }
    
    if choice in actions:
        actions[choice]()
    else:
        print(colored("Invalid choice. Exiting...", 'red'))
    
    input(colored("\nPress Enter to continue...", 'grey'))
    main_menu()

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(colored("\nOperation cancelled by user", 'red'))
        sys.exit(0)
    except Exception as e:
        print(colored(f"\nAn error occurred: {str(e)}", 'red'))
        sys.exit(1)
