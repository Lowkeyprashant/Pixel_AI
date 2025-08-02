from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import os
import dotenv as mt
from time import time, sleep

env_vars = mt.dotenv_values(".env")
InputLanguages = env_vars.get("InputLanguages", "en-US").split(",")

HtmlCodeTemplate = '''<!DOCTYPE html>
<html lang="en">
<head><title>Speech Recognition</title></head>
<body>
<button id="start" onclick="startRecognition()">Start</button>
<button id="end" onclick="stopRecognition()">Stop</button>
<p id="output"></p>
<script>
let recognition;
const output = document.getElementById('output');
function startRecognition() {
    recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'LANG_PLACEHOLDER';
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        output.textContent = transcript;
    };
    recognition.start();
}
function stopRecognition() {
    if (recognition) recognition.stop();
}
</script>
</body>
</html>'''

os.makedirs("Data", exist_ok=True)
current_dir = os.getcwd()
html_path = os.path.join(current_dir, "Data", "Voice.html")
link = f"file://{html_path}"

chrome_options = Options()
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--headless=new")  

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
wait = WebDriverWait(driver, 10)

TempDirPath = os.path.join(current_dir, "Frontend", "Files")
os.makedirs(TempDirPath, exist_ok=True)

def SetAssistantStatus(Status):
    with open(os.path.join(TempDirPath, "Status.data"), "w", encoding='utf-8') as file:
        file.write(Status)

def QueryModifier(Query):
    new_query = Query.strip().lower()
    if new_query and new_query[-1] not in ['?', '.', '!']:
        if any(w in new_query.split() for w in ["what", "who", "when", "where", "how", "why"]):
            return new_query.capitalize() + '?'
        else:
            return new_query.capitalize() + '.'
    return new_query.capitalize()

def UniversalTranslator(Text):
    return Text

def load_html(lang_code):
    html = HtmlCodeTemplate.replace("LANG_PLACEHOLDER", lang_code)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

def SpeechRecognition(lang_code):
    try:
        load_html(lang_code)
        driver.get(link)
        sleep(1)

        driver.execute_script("startRecognition();")

        start_time = time()
        while time() - start_time < 6:
            output = driver.find_element(By.ID, "output").text.strip()
            if output:
                driver.execute_script("stopRecognition();")
                if "en" in lang_code.lower():
                    return QueryModifier(output)
                else:
                    SetAssistantStatus("Translating...")
                    return QueryModifier(UniversalTranslator(output))
            sleep(0.3)

        driver.execute_script("stopRecognition();")
        return None

    except Exception as e:
        print(f"[{lang_code}] Error: {e}")
        return None

if __name__ == "__main__":
    while True:
        for lang in InputLanguages:
            result = SpeechRecognition(lang)
            if result:                                                                                                                                                                 
                print(f"[{lang}] → {result}")
                break
        else:
            print("No speech detected.")
        sleep(1)
