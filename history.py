import os
import json
import time
from termcolor import colored  # Added to match main script

# File paths updated to match main script
history = "/data/data/com.termux/files/home/history.txt"
temp = '/data/data/com.termux/files/home/temp.txt'
main_script = '/data/data/com.termux/files/home/main.py'  # Added main script path

def history_mod():
    if not os.path.isfile(history):
        print(colored("History is Not Yet Created! or History got deleted!!", 'red'))
        print(colored("Download at least once to create history and make sure Incognito Mode is turned off!!\n", 'yellow'))
        exit()
    
    start = time.time()
    histlist = []
    
    try:
        with open(history, 'r+', encoding='utf-8') as f:  # Added encoding
            for jsonObj in f:
                try:
                    Dict = json.loads(jsonObj)
                    histlist.append(Dict)
                except json.JSONDecodeError:
                    continue
        
        print("\n" + colored("History:", 'green') + "\n")
        for i in histlist:
            print(colored(i["SNo"]+")", 'cyan'), i["Name"]+" ||", colored(i["Site"], 'magenta'))
        
        end = time.time()
        print(f"\nListing time: {(end-start)*10**3:.02f}ms\n")
        
        print(colored("\nWhat would you like to do?", 'yellow'))
        print("1. Redownload from history")
        print("2. Revisit the download site")
        print("3. Clear history")
        print(colored("Press Enter to exit", 'grey'))
        
        choice = input("\nYour choice: ").strip()
        
        if choice == "1":
            ask = input("\nEnter the SNo: ").strip()
            output_dict = [a for a in histlist if a["SNo"] == ask]
            if not output_dict:
                print(colored("Invalid selection!", 'red'))
                exit()
                
            for j in output_dict:
                print(colored("\nSelected:", 'green'))
                print(j["SNo"]+")", j["Name"]+" ||", j["Site"])
                url = j["URL"]
                os.system(f'python {main_script} "{url}"')
                exit()
                
        elif choice == "2":
            ask = input("\nEnter the SNo: ").strip()
            output_dict = [a for a in histlist if a["SNo"] == ask]
            if not output_dict:
                print(colored("Invalid selection!", 'red'))
                exit()
                
            for j in output_dict:
                url = j["URL"]
                os.system(f'termux-open-url "{url}"')
                exit()
                
        elif choice == "3":
            confirm = input("\nType 'YES' to confirm clearing history: ").strip()
            if confirm == "YES":
                os.remove(history)
                print(colored("History cleared successfully!", 'green'))
            exit()
            
    except Exception as e:
        print(colored(f"\nError reading history: {str(e)}", 'red'))
        exit()

def temp_mod():
    try:
        with open(temp, 'r', encoding='utf-8') as f:  # Added encoding
            temp_link = f.read().strip()
            
        print(colored("\nPreviously failed download link:", 'yellow'))
        print(colored(temp_link, 'cyan') + "\n")
        
        print(colored("What would you like to do?", 'yellow'))
        print("1. Resume/retry download")
        print("2. Open the link in browser")
        print(colored("Press Enter to exit", 'grey'))
        
        sel = input("\nEnter your choice: ").strip()
        
        if sel == "1":
            print(colored("\nAttempting redownload...", 'green'))
            os.system(f'python {main_script} "{temp_link}"')
        elif sel == "2":
            print(colored("\nOpening link in browser...", 'green'))
            os.system(f'termux-open-url "{temp_link}"')
        else:
            print(colored("Skipping...", 'grey'))
            exit()
            
    except Exception as e:
        print(colored(f"\nError reading temp file: {str(e)}", 'red'))
        exit()

# Main execution flow
try:
    if os.path.isfile(temp):
        prompt = colored("\nA previously failed download exists. Resume it?", 'yellow')
        prompt += colored("\nType 'y' to resume or any key to view history: ", 'grey')
        
        if input(prompt).strip().lower() == 'y':
            temp_mod()
        else:
            history_mod()
    else:
        history_mod()
        
except KeyboardInterrupt:
    print(colored("\nOperation cancelled by user", 'red'))
    exit()
except Exception as e:
    print(colored(f"\nAn unexpected error occurred: {str(e)}", 'red'))
    exit()
