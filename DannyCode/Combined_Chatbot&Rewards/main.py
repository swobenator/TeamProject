#Author: Bogdan Postolachi
#Group B
from operator import truediv
import openai #import for openai, allows to use the chatgpt API (Source: https://www.doprax.com/tutorial/a-step-by-step-guide-to-using-the-openai-python-api/#:~:text=This%20line%20imports%20the%20OpenAI,to%20interact%20with%20OpenAI's%20APIs.&text=This%20line%20creates%20an%20instance,to%20interact%20with%20the%20API.)
import os #alows functions that interact with the operating system (Source: https://www.geeksforgeeks.org/os-module-python-examples/)
import sys #access the command-line arguments (Source: https://www.geeksforgeeks.org/python-sys-module/)
import logging #makes python outputs log into a file (Source: https://www.simplilearn.com/tutorials/python-tutorial/python-logging#:~:text=Python%20import%20logging%20is%20a,even%20to%20a%20remote%20server.)
from dotenv import load_dotenv #reads key-value pairs from a .env file and can set them as environment variables (Source: https://pypi.org/project/python-dotenv/#:~:text=Python%2Ddotenv%20reads%20key%2Dvalue,following%20the%2012%2Dfactor%20principles.)
from datetime import datetime, timedelta #supplies classes for manipulating dates and times (Sources: https://docs.python.org/3/library/datetime.html)
import json
import logging
from pathlib import Path

#Kivy Imports
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
import logging
from datetime import datetime, timedelta
from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.label import Label
from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivymd.toast import toast


# Fixed window size
Window.size = (400, 720)


#Rewards Page
#Author: Bogdan Postolachi
#Group B
# Constants
REWARDS_FILE = "rewards.json"
DAILY_REWARD_COINS = 10
MILESTONE_BONUS = {
    7: 25,
    14: 50,
    30: 100
}

logging.basicConfig(level=logging.INFO)



class RewardsManager:
    def __init__(self, file_path=REWARDS_FILE):
        self.file_path = Path(file_path)
        self.data = self.load_rewards()

    def load_rewards(self):
        if self.file_path.exists():
            try:
                with open(self.file_path, "r") as file:
                    return json.load(file)
            except json.JSONDecodeError:
                logging.error("Invalid JSON in rewards file", exc_info=True)
        return {"coins": 0, "streak": 0, "last_login": "", "login_history": []}

    def save_rewards(self):
        with open(self.file_path, "w") as file:
            json.dump(self.data, file, indent=4)

    def update_rewards(self):
        today = datetime.now().date()
        today_str = today.strftime("%d-%m-%Y")
        last_login = self.data.get("last_login")

        if last_login:
            last_date = datetime.strptime(last_login, "%d-%m-%Y").date()
            if last_date == today:
                return self.data, None
            elif last_date == today - timedelta(days=1):
                self.data["streak"] += 1
            else:
                self.data["streak"] = 1
        else:
            self.data["streak"] = 1

        reward = DAILY_REWARD_COINS
        bonus = MILESTONE_BONUS.get(self.data["streak"], 0)
        reward += bonus

        self.data["coins"] += reward
        self.data["last_login"] = today_str

        if today_str not in self.data["login_history"]:
            self.data["login_history"].append(today_str)

        # Calculate milestones
        self.data["milestones"] = self.data["streak"] // 7

        self.save_rewards()
        return self.data, bonus


class RewardsScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(lambda dt: self.update_display(), 0.1)

    def update_display(self):
        manager = RewardsManager()
        rewards, bonus = manager.update_rewards()

        self.ids.coin_amount.text = str(rewards["coins"])
        self.ids.streak_amount.text = str(rewards["streak"])
        self.ids.milestone_amount.text = str(rewards["milestones"])  # Update milestone count

        message = f"Milestone! +{bonus} bonus coins!" if bonus else "Rewards Updated"
        toast(message, duration=2)

    def show_history(self):
        manager = RewardsManager()
        history_text = "\n".join(manager.data["login_history"][-7:]) or "No history found."
        self.dialog = MDDialog(
            title="Login History",
            text=history_text,
            buttons=[
                MDRaisedButton(text="Close", on_release=lambda x: self.dialog.dismiss())
            ],
        )
        self.dialog.open()

    def open_calendar(self):
        manager = RewardsManager()
        history = set(manager.data.get("login_history", []))

        # Create the grid layout dynamically
        content = GridLayout(cols=7, rows=5, padding=dp(5), spacing=dp(5), size_hint=(None, None),
                             size=(dp(320), dp(280)))

        # Adding labels for the days of the month (1 to 31)
        for i in range(1, 32):
            day = f"{i:02d}-{datetime.now().month:02d}-{datetime.now().year}"
            label = Label(
                text=str(i),
                color=(1, 0, 0, 1) if day in history else (0.4, 0.4, 0.4, 1),  # Highlight login days in red
                font_size="16sp",
                size_hint=(None, None),
                size=(dp(40), dp(40)),
                halign="center",
                valign="middle",
            )
            content.add_widget(label)

        # Create the dialog with updated size and padding
        self.calendar_dialog = MDDialog(
            title="Login Calendar",
            type="custom",
            content_cls=content,
            size_hint=(None, None),
            size=(dp(340), dp(340)),  # Slightly larger dialog to fit numbers
            buttons=[
                MDRaisedButton(text="Close", on_release=lambda x: self.calendar_dialog.dismiss())
            ]
        )
        self.calendar_dialog.open()



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



class ChatbotScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = openai.OpenAI(api_key=API_KEY)
        self.chat_history = self.load_chat_history()
    # function to write logs
    # user_input - user messages
    # chat_response - bot responses
    def log_chat(self, user_input, chat_response):
        # appends chat logs to the file with timestamps.
        # Source: https://stackoverflow.com/questions/4706499/how-do-i-append-to-a-file
        # Original Code:
        """with open("test.txt", "a") as myfile:
                myfile.write("appended text")"""
        with open(log_filename, "a") as log_file:  # opens the file for appending ("a" mode).
            log_file.write(
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n")  # gets the date and time and formats it into readable string
            log_file.write(f"User: {user_input}\n")
            log_file.write(f"Zen Bot: {chat_response}\n\n")

    def load_chat_history(self):
        # Loads past chat history from the log file.
        self.chat_history = []
        if os.path.exists("chat_log.txt"):
            with open("chat_log.txt", "r", encoding="utf-8") as log_file:
                lines = log_file.readlines()
                for i in range(len(lines)):
                    if lines[i].startswith("User:"):
                        user_message = lines[i].replace("User:", "").strip()
                        self.chat_history.append({"role": "user", "content": user_message})
                    elif lines[i].startswith("MentalHealthBot:"):
                        bot_message = lines[i].replace("Zen Bot:", "").strip()
                        self.chat_history.append({"role": "assistant", "content": bot_message})
        return self.chat_history


    def chat_gpt(self, prompt):
        """Handles conversation with ChatGPT."""
        try:
            self.chat_history.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a mental health advisor. Your role is to help users dealing with mental health issues and provide support. All of your responses should be under 75 words."}
                ] + self.chat_history[-10:],  # Only keep the last 10 messages
                temperature=0.7,
                max_tokens=150
            )

            message = response.choices[0].message.content
            self.chat_history.append({"role": "assistant", "content": message})

            # Log the conversation
            self.log_chat(prompt, message)

            return message
        except openai.APIConnectionError as e:
            logging.error(f"API Connection Error: {e}")
            return "I'm sorry, but I encountered an error. Please try again later."

    def send_message(self):
        """Handles user input, sends it to GPT, and updates UI."""
        try:

            user_input = self.ids.user_input.text.strip()

            if not user_input:
                print("Warning: User input is empty, ignoring send request.")
                return

            bot_response = self.chat_gpt(user_input)

            # Display user and bot messages
            self.display_message("You", user_input, align="right")
            self.display_message("Zen Bot", bot_response, align="left")

            self.ids.user_input.text = ""

        except Exception as e:
            print(f"ERROR in send_message: {e}")

    def display_message(self, sender, message, align="left"):
        chat_box = self.ids.chat_box

        label = Label(
            text=f"[b]{sender}[/b]\n{message}",
            markup=True,
            size_hint=(None, None),
            text_size=(self.width * 0.7, None),
            halign=align,
            valign="top",
            font_size=16,
            color=(0, 0, 0, 1),
            padding=(10, 10)
        )

        def finalize_layout(_):
            label.height = label.texture_size[1] + 20
            label.width = label.texture_size[0]

            container = BoxLayout(
                size_hint_y=None,
                height=label.height + 20,
                orientation="horizontal",
                padding=[10, 5],
            )

            if align == "right":
                container.add_widget(Widget())
                container.add_widget(label)
            else:
                container.add_widget(label)
                container.add_widget(Widget())

            chat_box.add_widget(container)
            chat_box.height += container.height + 10
            self.ids.chat_scroll.scroll_y = 0

        # Delay to allow Kivy to calculate texture_size first
        Clock.schedule_once(finalize_layout, 0)


class ZenFlowApp(MDApp):
    """Main chatbot application."""

    def build(self):
        """Initializes the ScreenManager and loads the chatbot screen."""
          # Load chat history on startup
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        return Builder.load_file("main.kv")


if __name__ == "__main__":
    ZenFlowApp().run()