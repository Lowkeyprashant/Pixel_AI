from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import asyncio
import keyboard
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

classes = [
    "zCubwf", "hgKElc", "LTK00 sY7ric", "Z0LcW", "gsrt vk_bk FzvWSb YwPhnf", "pclqee",
    "tw-Data-text tw-text-small tw-ta", "IZ6rdc", "05uR6d LTK00", "vlzY6d",
    "webanswers-webanswers_table_webanswers-table", "dDoNo ikb4Bb gsrt", "sXLa0e",
    "LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"
]

useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"

client = Groq(api_key=GroqAPIKey)

professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need-don't hesitate to ask.",
]

messages = []

SystemChatBot = [{
    "role": "system",
    "content": f"hello, I am {os.environ.get('Username', 'AI Assistant')}. You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, etc."
}]

def GoogleSearch(Topic):
    try:
        search(Topic)
        return True
    except Exception as e:
        logging.error(f"GoogleSearch failed: {e}")
        return False

def Content(Topic):
    def OpenNotepad(File):
        default_text_editor = "notepad.exe"
        subprocess.Popen([default_text_editor, File])

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"})
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        return Answer

    Topic = Topic.replace("Content", "")
    ContentByAI = ContentWriterAI(Topic)

    file_path = rf"Data\{Topic.lower().replace(' ', '_')}.txt"
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(ContentByAI)
        OpenNotepad(file_path)
        return True
    except Exception as e:
        logging.error(f"Content writing failed: {e}")
        return False

def YouTubeSearch(Topic):
    try:
        Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
        webbrowser.open(Url4Search)
        return True
    except Exception as e:
        logging.error(f"YouTubeSearch failed: {e}")
        return False

def PlayYoutube(query):
    try:
        playonyt(query)
        return True
    except Exception as e:
        logging.error(f"PlayYoutube failed: {e}")
        return False

def openApp(app, sess=requests.Session()):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except Exception as e:
        logging.warning(f"App open failed for '{app}': {e}")
        # Fallback: Try searching for the app online
        def extract_links(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', {'jsname': 'UWckNb'})
            return [link.get('href') for link in links]

        def search_google(query):
            url = f"https://www.google.com/search?q={query}"
            headers = {"User-Agent": useragent}
            response = sess.get(url, headers=headers)
            if response.status_code == 200:
                return response.text
            else:
                logging.error("Failed to retrieve search results.")
                return None

        html = search_google(app)
        if html:
            links = extract_links(html)
            if links:
                webopen(links[0])
        return True

def closeApp(app):
    if "chrome" in app:
        # Optionally handle chrome closing differently
        return True
    try:
        close(app, match_closest=True, output=True, throw_error=True)
        return True
    except Exception as e:
        logging.error(f"closeApp failed: {e}")
        return False

def System(command):
    def mute():
        keyboard.press_and_release("volume mute")
    def unmute():
        keyboard.press_and_release("volume mute")
    def volume_up():
        keyboard.press_and_release("volume up")
    def volume_down():
        keyboard.press_and_release("volume down")

    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volume up":
        volume_up()
    elif command == "volume down":
        volume_down()
    else:
        logging.warning(f"Unknown system command: {command}")
    return True

async def TranslateAndExecute(commands: list[str]):
    command_map = {
        "open ": lambda arg: asyncio.to_thread(openApp, arg),
        "close ": lambda arg: asyncio.to_thread(closeApp, arg),
        "play ": lambda arg: asyncio.to_thread(PlayYoutube, arg),
        "content ": lambda arg: asyncio.to_thread(Content, arg),
        "google search ": lambda arg: asyncio.to_thread(GoogleSearch, arg),
        "Youtube ": lambda arg: asyncio.to_thread(YouTubeSearch, arg),
        "system ": lambda arg: asyncio.to_thread(System, arg),
    }
    funcs = []
    for command in commands:
        matched = False
        for prefix, func in command_map.items():
            if command.startswith(prefix):
                arg = command.removeprefix(prefix)
                funcs.append(func(arg))
                matched = True
                break
        if not matched:
            logging.warning(f"No Function Found for: {command}")
            print(f"No Function Found. For {command}")

    results = await asyncio.gather(*funcs)
    for result in results:
        yield result

async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass

if __name__ == "__main__":
    asyncio.run(Automation(["open facebook", "open Instagram", "play afsanay"]))

