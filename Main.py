from Frontend.GUI import (
    GraphicalUserInterface,
    set_assistant_status as SetAssistantStatus,
    show_text_to_screen as ShowTextToScreen,
    temp_directory_path as TempDirectoryPath,
    set_microphone_status as SetMicrophoneStatus,
    answer_modifier as AnswerModifier,
    query_modifier as QueryModifier,
    get_microphone_status as GetMicrophoneStatus,
    get_assistant_status as GetAssistantStatus,
)
from PyQt5.QtWidgets import QApplication
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import Chatbot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from time import sleep as Sleep
import subprocess
import threading
import json
import os
import sys
import asyncio

env_vars = dotenv_values(".env")
Username = env_vars.get("USERNAME", "User")
AssistantName = env_vars.get("AssistantName", "Assistant")
DefaultMessage = f'''{Username} : I am {AssistantName}, How are you?
{AssistantName} : Welcome {Username}, I am doing well. How may I help you?'''
subprocesses = []
Functions = ["open", "close", "minimize", "play", "system", "content", "google search", "Youtube"]

def ShowDefaultChatIfNoChat():
    try:
        with open(r'Data\ChatLog.json', "r", encoding='utf-8') as File:
            if len(File.read()) < 5:
                with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
                    file.write(DefaultMessage)
    except FileNotFoundError:
        os.makedirs("Data", exist_ok=True)
        with open(r'Data\ChatLog.json', "w", encoding='utf-8') as File:
            File.write("[]")
        with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
            file.write(DefaultMessage)

def ReadChatLogJson():
    with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
        chatlog_data = json.load(file)
    return chatlog_data

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry['role'] == 'user':
            formatted_chatlog += f"{Username}: {entry['content']}\n"
        elif entry['role'] == "assistant":
            formatted_chatlog += f"{AssistantName}: {entry['content']}\n"
    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatsOnGUI():
    with open(TempDirectoryPath('Database.data'), "r", encoding='utf-8') as File:
        Data = File.read()
    if len(str(Data)) > 0:
        lines = Data.split('\n')
        result = '\n'.join(lines)
        with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as File2:
            File2.write(result)
        ShowTextToScreen(result)

def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChat()
    ChatLogIntegration()
    ShowChatsOnGUI()

InitialExecution()

def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    SetAssistantStatus("Listening")
    Query = SpeechRecognition("en-US")
    if not Query or Query.strip() == "":
        SetAssistantStatus("Available")
        return

    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Thinking")
    Decision = FirstLayerDMM(Query)

    print("")
    print(f"Decision : {Decision}")
    print("")

    G = any([i for i in Decision if i.startswith("general")])
    R = any([i for i in Decision if i.startswith("realtime")])

    Merged_query = " and ".join(
        [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )

    for queries in Decision:
        if "generate " in queries:
            ImageGenerationQuery = str(queries)
            ImageExecution = True

    for queries in Decision:
        if TaskExecution is False:
            if any(queries.startswith(func) for func in Functions):
                threading.Thread(target=lambda: asyncio.run(Automation(list(Decision))), daemon=True).start()
                TaskExecution = True

    if ImageExecution is True:
        with open(r"Frontend\Files\ImageGeneration.data", "w") as file:
            file.write(f"{ImageGenerationQuery}, True")

        try:
            p1 = subprocess.Popen(['python', r'Backend\ImageGeneration.py'],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    stdin=subprocess.PIPE,  shell=False)
            subprocesses.append(p1)
        except Exception as e:
            print(f"Error in Image Generation: {e}")

    if G and R or R:
        SetAssistantStatus("Searching")
        Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
        ShowTextToScreen(f"{AssistantName} : {Answer}")
        AppendToChatLog('user', Query)
        AppendToChatLog('assistant', Answer)
        ChatLogIntegration()
        ShowChatsOnGUI()
        SetAssistantStatus("Answering")
        TextToSpeech(Answer)
        SetAssistantStatus("Available")
        return True

    else:
        for Queries in Decision:
            if "general " in Queries:
                SetAssistantStatus("Thinking")
                QueryFinal = Queries.replace("general ", "")
                Answer = Chatbot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{AssistantName} : {Answer}")
                AppendToChatLog('user', Query)
                AppendToChatLog('assistant', Answer)
                ChatLogIntegration()
                ShowChatsOnGUI()
                SetAssistantStatus("Answering")
                TextToSpeech(Answer)
                SetAssistantStatus("Available")
                return True

            elif "realtime " in Queries:
                SetAssistantStatus("Searching")
                QueryFinal = Queries.replace("realtime ", "")
                Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{AssistantName} : {Answer}")
                AppendToChatLog('user', Query)
                AppendToChatLog('assistant', Answer)
                ChatLogIntegration()
                ShowChatsOnGUI()
                SetAssistantStatus("Answering")
                TextToSpeech(Answer)
                SetAssistantStatus("Available")
                return True

            elif "exit" in Queries:
                QueryFinal = " Okay, Bye!"
                Answer = Chatbot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{AssistantName} : {Answer}")
                AppendToChatLog('user', Query)
                AppendToChatLog('assistant', Answer)
                ChatLogIntegration()
                ShowChatsOnGUI()
                SetAssistantStatus("Answering")
                TextToSpeech(Answer)
                SetAssistantStatus("Available")
                os._exit(1)

def AppendToChatLog(role, content):
    chatlog_path = r'Data\ChatLog.json'
    try:
        with open(chatlog_path, 'r', encoding='utf-8') as file:
            chatlog = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        chatlog = []
    chatlog.append({'role': role, 'content': content})
    with open(chatlog_path, 'w', encoding='utf-8') as file:
        json.dump(chatlog, file, ensure_ascii=False, indent=2)

def FirstThread():
    while True:
        CurrentStatus = GetMicrophoneStatus()
        if CurrentStatus == "True":
            SetAssistantStatus("Available")
            MainExecution()
        else:
            AIStatus = GetAssistantStatus()
            if "Available" in AIStatus:
                Sleep(0.05)  # Faster status polling
            else:
                SetAssistantStatus("Available")

def run_gui():
    app = QApplication(sys.argv)
    window = GraphicalUserInterface()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    thread1 = threading.Thread(target=FirstThread, daemon=True)
    thread1.start()
    run_gui()