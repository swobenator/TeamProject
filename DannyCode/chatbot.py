#Author: Bogdan Postolachi
#Group B

import openai #import for openai, allows to use the chatgpt API (Source: https://www.doprax.com/tutorial/a-step-by-step-guide-to-using-the-openai-python-api/#:~:text=This%20line%20imports%20the%20OpenAI,to%20interact%20with%20OpenAI's%20APIs.&text=This%20line%20creates%20an%20instance,to%20interact%20with%20the%20API.)
import os #alows functions that interact with the operating system (Source: https://www.geeksforgeeks.org/os-module-python-examples/)
import sys #access the command-line arguments (Source: https://www.geeksforgeeks.org/python-sys-module/)
import logging #makes python outputs log into a file (Source: https://www.simplilearn.com/tutorials/python-tutorial/python-logging#:~:text=Python%20import%20logging%20is%20a,even%20to%20a%20remote%20server.)
from dotenv import load_dotenv #reads key-value pairs from a .env file and can set them as environment variables (Source: https://pypi.org/project/python-dotenv/#:~:text=Python%2Ddotenv%20reads%20key%2Dvalue,following%20the%2012%2Dfactor%20principles.)
from datetime import datetime #supplies classes for manipulating dates and times (Sources: https://docs.python.org/3/library/datetime.html)

#Kivy Imports
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivymd.app import MDApp
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.widget import Widget
from kivy.uix.bubble import Bubble




#specifies the window size
Window.size = (400, 720)



#Chose to use a .env file (environment variable) for better security and is a standard
#Source: https://www.datacamp.com/tutorial/python-environment-variables
#Source: https://blog.devgenius.io/why-a-env-7b4a79ba689
#Loads environment variable
#Loads the .env file which stores the API Key
load_dotenv(dotenv_path="chatbot_api.env") #specifies the .env file to access

# Gets API Key from .env file
API_KEY = os.getenv("OPENAI_API_KEY")

#Error message in case API Key can't be accesed
if not API_KEY:
    print("Error: API Key not found")
    sys.exit(1) #Stops the program, exit(1) indicates an error happened(Source: https://stackoverflow.com/questions/9426045/difference-between-exit0-and-exit1-in-python)

# Chat Logging
#All log messages will be written to chat_log.txt
#If the file doesn’t exist it will be created
#Source: https://docs.python.org/3/library/logging.config.html
log_filename = "chat_log.txt"

#Log Configuration Code inspired from source mentioned above
#Original Code:
"""formatters:
  brief:
    format: '%(message)s'
  default:
    format: '%(asctime)s %(levelname)-8s %(name)-15s %(message)s'
    datefmt: '%Y-%m-%d %H:%M:%S'
  custom:
      (): my.package.customFormatterFactory
      bar: baz
      spam: 99.9
      answer: 42"""

logging.basicConfig(
    filename=log_filename,
    level=logging.INFO, #minimum security level of messages to log
    format="%(asctime)s - %(message)s", #defines how each log message will be formatted
    datefmt="%Y-%m-%d %H:%M:%S", #Specifies how the timestamp should be displayed
)

#OpenAI client
client = openai.OpenAI(api_key=API_KEY)

#function to write logs
#user_input - user messages
#chat_response - bot responses
def log_chat(user_input, chat_response):
    #appends chat logs to the file with timestamps.
    #Source: https://stackoverflow.com/questions/4706499/how-do-i-append-to-a-file
    #Original Code:
    """with open("test.txt", "a") as myfile:
            myfile.write("appended text")"""
    with open(log_filename, "a") as log_file: #opens the file for appending ("a" mode).
        log_file.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n") #gets the date and time and formats it into readable string
        log_file.write(f"User: {user_input}\n")
        log_file.write(f"MentalHealthBot: {chat_response}\n\n")



def load_chat_history():
    #Loads past chat history from the log file.
    chat_history = []
    if os.path.exists("chat_log.txt"):
        with open("chat_log.txt", "r", encoding="utf-8") as log_file:
            lines = log_file.readlines()
            for i in range(len(lines)):
                if lines[i].startswith("User:"):
                    user_message = lines[i].replace("User:", "").strip()
                    chat_history.append({"role": "user", "content": user_message})
                elif lines[i].startswith("MentalHealthBot:"):
                    bot_message = lines[i].replace("MentalHealthBot:", "").strip()
                    chat_history.append({"role": "assistant", "content": bot_message})
    return chat_history



"""def chat_gpt(prompt, chat_history=[]):
    try:
        chat_history.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model="gpt-3.5-turbo", #ChatGPT model

            # Specifying to the bot that it can only talk about mental health
            # Source: https://ihsavru.medium.com/how-to-build-your-own-custom-chatgpt-using-python-openai-78e470d1540e
            messages=[
                {"role": "system", "content": "You are a mental health advisor. Your role is to help users dealing with mental health issues and provide support. Be concise in your responses."}
            ] + chat_history,  #maintain conversation history
            temperature=0.7,
            max_tokens=150
        )

        message = response.choices[0].message.content
        chat_history.append({"role": "assistant", "content": message})

        # Log conversation
        log_chat(prompt, message)

        return message
    except openai.APIConnectionError as e:
        logging.error(f"API Connection Error: {e}")
        return "I'm sorry, but I encountered an error. Please try again later."""""



#Test Lines
# Start Chat
#print("MentalHealthBot: Hello! How can I help you today? (Type 'exit' to quit)")
#chat_history = []

"""while True:
    try:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("MentalHealthBot: Goodbye! Take care!")
            break

        response = chat_gpt(user_input, chat_history)
        print("MentalHealthBot:", response)

    except KeyboardInterrupt:
        print("\nMentalHealthBot: Goodbye!")
        break"""



class ChatbotScreen(Screen):
    #Chatbot Screen for messages
    pass


# Load KV file
if not Builder.load_file("chatbot.kv"):
    print("Could not load chatbot.kv")


class ChatbotApp(MDApp):
    """Main chatbot application."""

    def build(self):
        """Initializes the ScreenManager and loads the chatbot screen."""
        self.chat_history = load_chat_history()  # Load chat history on startup
        sm = ScreenManager()
        sm.add_widget(ChatbotScreen(name="chatbot_screen"))
        return sm

    def chat_gpt(self, prompt):
        """Handles conversation with ChatGPT."""
        try:
            self.chat_history.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a mental health advisor. Your role is to help users dealing with mental health issues and provide support. Be concise in your responses."}
                ] + self.chat_history[-10:],  # Only keep the last 10 messages
                temperature=0.7,
                max_tokens=150
            )

            message = response.choices[0].message.content
            self.chat_history.append({"role": "assistant", "content": message})

            # Log the conversation
            log_chat(prompt, message)

            return message
        except openai.APIConnectionError as e:
            logging.error(f"API Connection Error: {e}")
            return "I'm sorry, but I encountered an error. Please try again later."

    def send_message(self):
        """Handles user input, sends it to GPT, and updates UI."""
        try:
            screen = self.root.get_screen("chatbot_screen")
            user_input = screen.ids.user_input.text.strip()

            if not user_input:
                print("Warning: User input is empty, ignoring send request.")
                return

            self.display_message("You", user_input, align="right")

            bot_response = self.chat_gpt(user_input)

            self.display_message("MentalHealthBot", bot_response, align="left")

            screen.ids.user_input.text = ""

        except Exception as e:
            print(f"ERROR in send_message: {e}")

    def display_message(self, sender, message, align="left"):
        """Displays messages in a clean, professional chat format."""
        try:
            chat_box = self.root.get_screen("chatbot_screen").ids.chat_box

            # Create a message container
            message_container = BoxLayout(
                size_hint_y=None,
                padding=[120, 5],
                spacing=10,
                orientation="horizontal"
            )

            # Label for message text
            label = Label(
                text=f"[b]{sender}:[/b] {message}",
                size_hint_x=0.75,
                size_hint_y=None,
                markup=True,
                text_size=(self.root.width * 0.7, None),
                halign="left" if align == "left" else "right",
                valign="middle",
                font_size=16,
                color=(0, 0, 0, 1) if align == "right" else (0, 0, 0, 1),  # White text for user, black for bot
                padding=(12, 8)
            )

            label.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1] + 10))

            if align == "right":
                message_container.add_widget(Widget())  # Push right
                message_container.add_widget(label)
            else:
                message_container.add_widget(label)
                message_container.add_widget(Widget())  # Push left

            chat_box.add_widget(message_container)
            chat_box.height += label.height + 20

            self.root.get_screen("chatbot_screen").ids.chat_scroll.scroll_y = 0

        except Exception as e:
            print(f"ERROR in display_message: {e}")


if __name__ == "__main__":
    ChatbotApp().run()