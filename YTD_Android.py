#Version 10.2.0.0
#Engine 10.2
#Stable version

#(Master) imports
import os
import sys
import linecache
import json
from termcolor import colored
from datetime import date
import requests
from bs4 import BeautifulSoup

#Version Info:
version = (linecache.getline(linecache.sys.argv[0],1))
print(version.replace("#", ""))
linecache.clearcache()

#Engine info:
engine = (linecache.getline(linecache.sys.argv[0],2))
print(engine.replace("#", ""))
linecache.clearcache()

#Build info:
build = (linecache.getline(linecache.sys.argv[0],3))
print("Build: "+ build.replace("#", ""))
linecache.clearcache()

#(Default) JSON file creation or verification:
json_path = "/data/data/com.termux/files/home/default.json"

# ... [keep all your existing code until the audio function] ...

#(Youtube) Audio
def audio(dir):
    print("Downloading songs from "+dir+": \n")
    with open(json_path, "r") as defaultFile:
        data = json.load(defaultFile)
        
    #json key first time allotment
    if data["default"][0]["codec"] == "":
        print('Enter the Format of audio (mp3, aac, m4a, flac....)')
        firstCodec = input('Enter the format: ')
        data["default"][0]["codec"] = firstCodec
    
        with open(json_path, "w") as defaultFile:
            json.dump(data, defaultFile)
        defaultFile.close

        with open(json_path, "r") as default:
            data = json.load(default)
            codec = data["default"][0]["codec"]
        default.close
    
    #json key for later use
    else:
        with open(json_path, "r") as default:
            data = json.load(default)
            notification = data["default"][0]["codec"]
            choice = input("Default audio codec is " +notification+ ". If you need to download in different codec type (y) or else skip:")
            print("\n")
            if choice == "y":
                print('Enter the Format of audio (mp3, aac, m4a, flac....)\n')
                lateCodec = input('Enter the format: ')
                print("\n")                
                with open(json_path, "r") as defaultFile:
                    data = json.load(defaultFile)
                    data["default"][0]["codec"] = lateCodec
                
                with open(json_path, "w") as defaultFile:
                    json.dump(data, defaultFile)
                defaultFile.close

                with open(json_path, "r") as defa:
                    data = json.load(defa)
                    codec = data["default"][0]["codec"]
                defa.close
            
            else:
                codec = data["default"][0]["codec"]
            default.close
    
    path = genPath+"Termux_Downloader/"+dir+"/"
    exist = os.path.isdir(path)
    if exist:
        pass
    else:
        os.mkdir(path)
        
    if "playlist" in link:
        op_path =  path + '/%(playlist)s/%(title)s.%(ext)s'
        thumb = bool(True)
    else:
        op_path =  path + '%(title)s.%(ext)s'     
        thumb = bool(True)
        
    opt = {
            'format' : 'bestaudio/best',
            'writethumbnail' : thumb,
            'ignoreerrors': True,
            'outtmpl': op_path,
            'postprocessors' :
                [
                    {
                        'key' : 'FFmpegExtractAudio',
                        'preferredcodec' : codec,
                    },
                    {
                        'key': 'FFmpegMetadata',
                        'add_metadata' : True,     
                    },
                    {
                        "key" : 'EmbedThumbnail',
                        'already_have_thumbnail'  : False,
                    }
                ]
             }
    if dir == "YTmusic":
        site = "Youtube Music"
    else:
        site = "Youtube"
    
    # Download the audio first
    downloader(opt, site=site)
    
    # Now try to download lyrics
    try:
        download_lyrics(link, path)
    except Exception as e:
        print(f"Could not download lyrics: {str(e)}")

def download_lyrics(video_url, save_path):
    """Function to download lyrics for a YouTube video"""
    import yt_dlp
    
    # Get video info to extract title
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        video_title = info.get('title', '')
    
    if not video_title:
        print("Could not get video title for lyrics search")
        return
    
    print(f"\nSearching lyrics for: {video_title}")
    
    # Try to find lyrics from various sources
    lyrics = None
    
    # Try Musixmatch
    try:
        lyrics = get_musixmatch_lyrics(video_title)
    except:
        pass
    
    # Try Genius as fallback
    if not lyrics:
        try:
            lyrics = get_genius_lyrics(video_title)
        except:
            pass
    
    if lyrics:
        # Save as .lrc file
        lrc_filename = os.path.join(save_path, f"{video_title}.lrc")
        with open(lrc_filename, 'w', encoding='utf-8') as f:
            f.write(lyrics)
        print(f"Lyrics saved as: {lrc_filename}")
    else:
        print("Could not find lyrics for this track")

def get_musixmatch_lyrics(song_title):
    """Try to get lyrics from Musixmatch"""
    base_url = "https://www.musixmatch.com/search/"
    search_url = base_url + song_title.replace(' ', '%20')
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find first result link
    first_result = soup.find('a', {'class': 'title'})
    if not first_result:
        return None
    
    lyrics_url = "https://www.musixmatch.com" + first_result['href']
    
    # Get lyrics page
    lyrics_response = requests.get(lyrics_url, headers=headers)
    lyrics_soup = BeautifulSoup(lyrics_response.text, 'html.parser')
    
    # Extract lyrics
    lyrics_div = lyrics_soup.find('div', {'class': 'mxm-lyrics'})
    if not lyrics_div:
        return None
    
    lyrics = ""
    for verse in lyrics_div.find_all('span', {'class': 'lyrics__content__ok'}):
        lyrics += verse.get_text() + "\n"
    
    return lyrics.strip()

def get_genius_lyrics(song_title):
    """Try to get lyrics from Genius"""
    base_url = "https://genius.com/api/search/multi?q="
    search_url = base_url + song_title.replace(' ', '%20')
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(search_url, headers=headers)
    data = response.json()
    
    # Find first song result
    song_hit = None
    for section in data['response']['sections']:
        if section['type'] == 'song':
            if section['hits']:
                song_hit = section['hits'][0]['result']
                break
    
    if not song_hit:
        return None
    
    lyrics_url = song_hit['url']
    
    # Get lyrics page
    lyrics_response = requests.get(lyrics_url, headers=headers)
    lyrics_soup = BeautifulSoup(lyrics_response.text, 'html.parser')
    
    # Extract lyrics
    lyrics_div = lyrics_soup.find('div', {'class': 'lyrics'})
    if not lyrics_div:
        return None
    
    return lyrics_div.get_text().strip()

# ... [keep all the remaining code unchanged] ...
