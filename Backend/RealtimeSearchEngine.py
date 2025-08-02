from googlesearch import search
from groq import Groq
import json
import datetime
from dotenv import dotenv_values
from pathlib import Path

DATA_PATH = Path("Data/ChatLog.json")

env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
AssistantName = env_vars.get("AssistantName")
GroqAPIkey = env_vars.get("GroqAPIKey")

groq = Groq(api_key=GroqAPIkey)

System = (
    f"Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {AssistantName} which has real-time up-to-date information from the internet.\n"
    "*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***\n"
    "*** Just answer the question from the provided data in a professional way. ***"
)

def load_messages():
    """Load chat messages from file."""
    if DATA_PATH.exists():
        with DATA_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_messages(messages):
    """Save chat messages to file."""
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DATA_PATH.open("w", encoding="utf-8") as f:
        json.dump(messages, f, indent=4)

def googleSearch(query):
    """Perform a Google search and format the results."""
    try:
        results = list(search(query, advanced=True, num_results=5))
    except Exception as e:
        return f"Error during search: {e}\n"
    answer = f"The search results for '{query}' are:\n\n"
    for i in results:
        answer += f"Title: {i.title}\nDescription: {i.description}\nURL: {i.url}\n\n"
    answer += "End of Search Results\n\n"
    return answer

def AnswerModifier(answer):
    """Remove empty lines from the answer."""
    return '\n'.join(line for line in answer.split('\n') if line.strip())

def Information():
    """Return formatted real-time date and time information."""
    now = datetime.datetime.now()
    return (
        "Use this Real-Time Information if needed:\n\n"
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\n"
        f"Time: {now.strftime('%H')} hours, {now.strftime('%M')} minutes, {now.strftime('%S')} seconds.\n"
    )

def RealtimeSearchEngine(prompt, messages=None, system_chatbot=None):
    """
    Main function to handle real-time search and chat.
    Args:
        prompt (str): User's query.
        messages (list): Chat history.
        system_chatbot (list): System prompt history.
    Returns:
        str: Assistant's answer.
    """
    if messages is None:
        messages = load_messages()
    if system_chatbot is None:
        system_chatbot = [
            {"role": "system", "content": System},
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello, how can I help you?"}
        ]

    messages.append({"role": "user", "content": f"!{prompt}"})
    search_results_content = googleSearch(prompt)
    system_chatbot.append({"role": "system", "content": search_results_content})

    try:
        completion = groq.chat.completions.create(
            model='llama3-70b-8192',
            messages=system_chatbot + [{'role': 'system', 'content': Information()}] + messages,
            temperature=0.7,
            max_tokens=2048,
            stream=True
        )
        answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content
        answer = AnswerModifier(answer.strip().replace("</s", ""))
    except Exception as e:
        answer = f"Error generating response: {e}"

    messages.append({"role": "assistant", "content": answer})
    save_messages(messages)
    system_chatbot.pop()
    return answer

if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        print(RealtimeSearchEngine(prompt))