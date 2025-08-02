Pixel_AI is a comprehensive AI assistant designed to interact with users through speech and text. It features a modular architecture that separates core functionalities such as speech-to-text, text-to-speech, a decision-making model, a chatbot, a real-time search engine, and automation capabilities. The assistant uses a PyQt5-based GUI for a seamless user experience, including a visual representation of the assistant's status.

Core Features
Speech-to-Text (STT): The SpeechToText.py module uses Selenium and a temporary HTML file to perform speech recognition in various languages. It listens for user commands and converts spoken words into a text query, which is then passed on to the decision-making model.

Decision-Making Model (DMM): The Model.py module acts as the central router for user queries. It uses a Cohere-based language model (command-r-plus) to categorize incoming queries into predefined actions like general, realtime, open, close, play, generate image, system, content, google search, Youtube, and reminder. This allows the assistant to determine whether to use its internal chatbot, perform a web search, or execute a local task.

Chatbot: The Chatbot.py module uses the Groq API and the llama3-70b-8192 model to handle general conversational queries. It maintains a chat log in a JSON file (Data\ChatLog.json) to provide context-aware responses and also incorporates real-time date and time information.

Real-time Search Engine: The RealtimeSearchEngine.py module is responsible for fetching up-to-date information. It utilizes the googlesearch-python library to perform a Google search and then passes the search results to a Groq-based model to formulate a professional and concise answer.

Text-to-Speech (TTS): The TextToSpeech.py module uses the edge_tts library to convert the assistant's text responses into natural-sounding speech. It can also handle long responses by truncating the spoken part and directing the user to the GUI for the full text.

Automation: The Automation.py module handles system-level tasks and automations. It can open and close applications and websites using AppOpener and webbrowser, play songs on YouTube via pywhatkit, and perform system commands like muting/unmuting the volume using the keyboard library. It can also generate content (e.g., letters, code) and save it to a file, which is then opened in Notepad.

Image Generation: The ImageGeneration.py module uses the Hugging Face API with the stabilityai/stable-diffusion-xl-base-1.0 model to generate images from a user-provided prompt. It saves the generated images locally and then opens them for the user to view.

GUI: The GUI.py module creates a graphical user interface using PyQt5. The GUI displays the chat history, the assistant's current status (e.g., "Listening," "Thinking"), and a microphone icon to toggle speech recognition.

Dependencies
The project's dependencies are listed in Requirements.txt. These libraries are crucial for the various functionalities of Pixel_AI:


python-dotenv: Manages environment variables.


groq: Provides access to the Groq language models.


AppOpener: Used for opening and closing applications.


pywhatkit: Facilitates YouTube and Google searches.


bs4 (Beautiful Soup) and requests: For web scraping and making HTTP requests.


pillow: Used for image manipulation, particularly for opening generated images.


rich: For enhanced terminal output.


keyboard: For sending system-level key presses.


cohere: Powers the decision-making model.


googlesearch-python: Performs Google searches.


selenium and webdriver-manager: Automates browser interactions for speech recognition.


edge_tts and pygame: Used for the text-to-speech functionality.


PyQt5: The framework for the graphical user interface.


pylance: A language server for Python.

Project Structure
├── Backend/
│   ├── Automation.py
│   ├── Chatbot.py
│   ├── ImageGeneration.py
│   ├── Model.py
│   ├── RealtimeSearchEngine.py
│   ├── SpeechToText.py
│   └── TextToSpeech.py
├── Data/
│   └── ChatLog.json
├── Frontend/
│   ├── Files/
│   │   ├── Database.data
│   │   ├── ImageGeneration.data
│   │   ├── Mic.data
│   │   └── Status.data
│   ├── Graphics/
│   │   ├── Jarvis.gif
│   │   └── ... (other icons)
│   └── GUI.py
├── .env
├── Main.py
└── Requirements.txt
Setup and Installation
Clone the repository:

git clone [repository_url]
cd Pixel_AI
Install dependencies:

pip install -r Requirements.txt
Configure API keys:
Create a .env file in the root directory and add your API keys for Groq, Cohere, and Hugging Face.

GroqAPIKey="your_groq_api_key"
CohereAPIKey="your_cohere_api_key"
HuggingFaceAPIKey="your_hugging_face_api_key"
Username="YourName"
AssistantName="AssistantName"
AssistantVoice="en-US-JennyNeural"
InputLanguages="en-US,hi-IN"
Run the application:

python Main.py
How It Works
Listening: The Main.py script starts the GUI and a separate thread for the main execution. The user can click the microphone icon in the GUI to activate the SpeechRecognition module, which listens for a voice command.

Processing: The spoken query is converted to text and passed to the FirstLayerDMM (Decision-Making Model).

Decision: The DMM analyzes the query and decides which module should handle it (e.g., Chatbot.py, RealtimeSearchEngine.py, or Automation.py).

Execution: The appropriate module is called to perform the task.

For a "general" query, the Chatbot provides a conversational response.

For a "realtime" query, the RealtimeSearchEngine performs a web search and summarizes the results.

For an "automation" query (e.g., "open Chrome"), the Automation module executes the command.

Responding: The response from the executed module is then passed to the TextToSpeech module to be spoken aloud. At the same time, the response is displayed in the GUI's chat window.

Loop: The system returns to a listening state, waiting for the next user command.
