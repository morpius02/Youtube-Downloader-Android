#!/bin/bash

# Installation script for Termux Downloader
# Version: 10.2.0.0
echo -e "\033[1;36mTermux Downloader Installation Script\033[0m"
echo -e "\033[1;34mVersion: 10.2.0.0\033[0m"
echo

# Check if running in Termux
if [ ! -d "/data/data/com.termux/files/home" ]; then
    echo -e "\033[1;31mError: This script must be run in Termux!\033[0m"
    exit 1
fi

# Function to display progress
progress() {
    echo -e "\033[1;32m$1\033[0m"
}

# Installing scripts
progress "[1/7] Installing main scripts..."
mv "refresh.sh" "/data/data/com.termux/files/home/refresh.sh"
mv "YTD_Android.py" "/data/data/com.termux/files/home/main.py"
mv "termux-url-opener" "/data/data/com.termux/files/home/termux-url-opener"
mv "updater.py" "/data/data/com.termux/files/home/updater.py"
mv "history.py" "/data/data/com.termux/files/home/history.py"
mv "patch0.1.py" "/data/data/com.termux/files/home/patch0.1.py"
mv "mod.txt" "/data/data/com.termux/files/usr/etc/motd"
mv "tools.py" "$PREFIX/bin/tools"
chmod +x "$PREFIX/bin/tools"

# Bin file creation and permission elevation
progress "[2/7] Setting up binaries..."
mkdir -p "/data/data/com.termux/files/home/bin"
mv "termux-url-opener" "/data/data/com.termux/files/home/bin/termux-url-opener"
chmod +x "/data/data/com.termux/files/home/bin/termux-url-opener"

# Storage permission
progress "[3/7] Setting up storage permissions..."
if [ -e '/data/data/com.termux/files/home/default.json' ]; then
    termux-setup-storage -y
    python "/data/data/com.termux/files/home/patch0.1.py"
else
    termux-setup-storage
    rm -f "/data/data/com.termux/files/home/patch0.1.py"
fi

# Binaries installation
if [ -e '/data/data/com.termux/files/home/noobjection.temp' ]; then
    # Update mode
    progress "[4/7] Running in update mode..."
    rm -f '/data/data/com.termux/files/home/noobjection.temp'
    
    # Install new dependencies for metadata features
    progress "[5/7] Installing new dependencies..."
    pip install mutagen pillow -U
    
    # Completion message
    echo
    echo -e "\033[1;32mUPDATE/UPGRADE SUCCESSFUL!\033[0m"
    
    # Cleanup
    progress "[6/7] Cleaning up..."
    rm -rf "/data/data/com.termux/files/home/Youtube-Downloader-Android"
    sleep 3
else
    # Fresh install mode
    progress "[4/7] Installing required packages..."
    pkg update -y
    pkg upgrade -y
    pkg install python aria2 ffmpeg -y
    
    progress "[5/7] Installing Python dependencies..."
    pip install --upgrade pip
    pip install beautifulsoup4 termcolor requests wheel yt-dlp ffmpeg gdown mutagen pillow
    
    # Remove conflicting packages
    apt remove rclone -y
    
    # Initialize the downloader
    progress "[6/7] Initializing downloader..."
    python "/data/data/com.termux/files/home/main.py" > /dev/null 2>&1
    
    # Final updates
    progress "[7/7] Performing final updates..."
    apt update -y
    apt upgrade -y
    apt autoremove -y
    
    # Display README
    if [ -f "/data/data/com.termux/files/home/Youtube-Downloader-Android/README.md" ]; then
        cat "/data/data/com.termux/files/home/Youtube-Downloader-Android/README.md"
    fi
    
    # Cleanup
    rm -rf "/data/data/com.termux/files/home/Youtube-Downloader-Android"
    
    # Completion message
    echo
    echo -e "\033[1;32mINSTALLATION SUCCESSFUL!\033[0m"
    echo -e "\033[1;33mNote: The new version includes automatic metadata tagging for audio files!\033[0m"
    sleep 5
fi

# Final cleanup
progress "[7/7] Finalizing installation..."
find "/data/data/com.termux/files/home" -name "*.temp" -delete
find "/data/data/com.termux/files/home" -name "*.bak" -delete

echo
echo -e "\033[1;34mInstallation completed successfully!\033[0m"
echo -e "\033[1;35mYou can now use the downloader by sharing links to Termux.\033[0m"
exit 0
