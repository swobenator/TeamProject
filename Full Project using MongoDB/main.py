# Learned how to use mongodb with python using the following resouces: https://www.w3schools.com/python/python_mongodb_getstarted.asp, https://www.mongodb.com/docs/languages/python/pymongo-driver/current/
from pymongo import MongoClient
from kivymd.uix.button import MDIconButton
from kivy.uix.popup import Popup
# Learned how to use graphs with kivy using this video: https://youtu.be/83C4tl8scoY?si=JHFL_Gbi276w0nkE
from kivy_garden.matplotlib import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
from kivy.uix.spinner import SpinnerOption
from bson import ObjectId
from kivy.core.audio import SoundLoader  # Loads and plays sound files.
from kivy.properties import NumericProperty, StringProperty  # Import that allows dynamic UI updates, Source:https://kivy.org/doc/stable/api-kivy.properties.html#kivy.properties.NumericProperty , https://kivy.org/doc/stable/api-kivy.properties.html#kivy.properties.StringProperty
from kivymd.uix.button import MDFlatButton  # Used this for a button in the pop-up
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.scrollview import ScrollView
from kivymd.uix.textfield import MDTextField
import uuid  # Genrates unique identifiers (UUIDS) to uniquely identify items
from kivy.properties import BooleanProperty
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
import openai  # import for openai, allows to use the chatgpt API (Source: https://www.doprax.com/tutorial/a-step-by-step-guide-to-using-the-openai-python-api/#:~:text=This%20line%20imports%20the%20OpenAI,to%20interact%20with%20OpenAI's%20APIs.&text=This%20line%20creates%20an%20instance,to%20interact%20with%20the%20API.)
import os  # alows functions that interact with the operating system (Source: https://www.geeksforgeeks.org/os-module-python-examples/)
import sys  # access the command-line arguments (Source: https://www.geeksforgeeks.org/python-sys-module/)
# import logging  # makes python outputs log into a file (Source: https://www.simplilearn.com/tutorials/python-tutorial/python-logging#:~:text=Python%20import%20logging%20is%20a,even%20to%20a%20remote%20server.)
from dotenv import load_dotenv  # reads key-value pairs from a .env file and can set them as environment variables (Source: https://pypi.org/project/python-dotenv/#:~:text=Python%2Ddotenv%20reads%20key%2Dvalue,following%20the%2012%2Dfactor%20principles.)
# supplies classes for manipulating dates and times (Sources: https://docs.python.org/3/library/datetime.html)
import json
import logging
from pathlib import Path
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from datetime import datetime, timedelta
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

Window.size = (400, 720)

# MongoDB Connection
client = MongoClient("mongodb://127.0.0.1:27017/")
# Accessing the database we want to work with
db = client["Kivy_app"]
# Accessing collections within the Kivy_app database
users_collection = db["users"]
mood_collection = db["mood_data"]
popup_collection = db["daily_popup"]
journals_collection = db["journal_data"]
habits_collection = db["habit_data"]
rewards_collection = db["rewards_data"]
chat_collection = db["chatlog_data"]


# Custom properties for the Spinner used in the
class CustomSpinnerOption(SpinnerOption):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0.2, 0, 1)
        self.color = (1, 1, 1, 1)
        self.font_size = "16sp"
        self.height = 40


SOUNDS_FOLDER = "sounds_folder"

# Rewards Page
# Author: Bogdan Postolachi

# Constant
DAILY_REWARD_COINS = 10  #amount of coins user gets every day they log in


# (https://www.w3schools.com/python/python_dictionaries.asp):
MILESTONE_BONUS = {  #dictionary that defines bounus coins for millestones
    7: 25,
    14: 50,
    30: 100
}

# logging module used to track events that happen while program runs
# reasource used for info: https://docs.python.org/3/library/logging.html
logging.basicConfig(level=logging.INFO)


# class manages & updates user daily rewards
# now saves & loads data from MongoDB instead of a JSON file
class RewardsManager:
    # constructor class - manages reward logic per user using their email address
    def __init__(self, user_email):
        self.user_email = user_email  # sets user email
        self.data = self.load_rewards()  # loads user's reward data from the database

    # loads user reward data
    def load_rewards(self):
        user_data = rewards_collection.find_one({"email": self.user_email})  # find reward entry by email
        if user_data:
            user_data.pop("_id", None)  # remove mongoDB's default object _id field
            return user_data
        else:
            # if the user has no existing data, create default entry
            default_data = {
                "email": self.user_email,
                "coins": 0,
                "streak": 0,
                "last_login": "",
                "login_history": [],
                "milestones": 0
            }
            rewards_collection.insert_one(default_data)  # insert default record
            return default_data

    # method saves the current rewards data back to MongoDB
    def save_rewards(self):
        rewards_collection.update_one(
            {"email": self.user_email},
            {"$set": self.data},
            upsert=True  # creates record if not found
        )

    # checks if user logged in today, updates streak, coins, milestones and login history
    def update_rewards(self):
        today = datetime.now().date()  # gets today's date
        today_str = today.strftime("%d-%m-%Y")  # converts date to string
        last_login = self.data.get("last_login")  # reads last_login value from rewards data

        # check log in streak
        if last_login:
            last_date = datetime.strptime(last_login, "%d-%m-%Y").date()
            if last_date == today:  # if user logged in today don't update
                return self.data, None
            elif last_date == today - timedelta(days=1):  # if user logged in yesterday add 1 streak
                self.data["streak"] += 1
            else:  # if user logged in longer than yesterday, reset streak to 1
                self.data["streak"] = 1
        else:  # if user's first ever login, make streak equal to 1
            self.data["streak"] = 1

        reward = DAILY_REWARD_COINS  # base reward for every new day is 10 coins
        bonus = MILESTONE_BONUS.get(self.data["streak"], 0)  # add the milestone bonus if any
        reward += bonus  # add the milestone bonus to the reward

        self.data["coins"] += reward  # add the coins
        self.data["last_login"] = today_str  # update the last_login

        if today_str not in self.data["login_history"]:  # stops duplicates of the same day
            self.data["login_history"].append(today_str)

        # calculates milestones
        self.data["milestones"] = self.data["streak"] // 7

        self.save_rewards()  # save updated reward data to the database
        return self.data, bonus


# custom screen in Kivy app
class RewardsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_email = None  # holds current user's email

    # method to be called from LoginScreen to set email
    def set_user(self, email):
        self.user_email = email

    # ensures data is fresh when the screen opens
    def on_enter(self):
        Clock.schedule_once(lambda dt: self.update_display(), 0.1)  # runs when user navigates to rewards screen

    # refreshes the rewards
    def update_display(self):
        if not self.user_email:
            logging.warning("No user email set for RewardsScreen")
            return

        manager = RewardsManager(self.user_email)  # creates instance using user email
        rewards, bonus = manager.update_rewards()  # calls update_rewards() method from RewardsManager

        self.ids.coin_amount.text = str(rewards["coins"])  # updates the text in the app using id from kivy file
        self.ids.streak_amount.text = str(rewards["streak"])
        self.ids.milestone_amount.text = str(rewards["milestones"])  # updates milestone count

        message = f"Milestone! +{bonus} bonus coins!" if bonus else "Rewards Updated"  # pop up message
        toast(message, duration=2)  # display the message through a toast

    # method shows the login history
    def show_history(self):
        manager = RewardsManager(self.user_email)
        history_text = "\n".join(manager.data["login_history"][-7:]) or "No history found."  # show last 7 entries
        self.dialog = MDDialog(  # popup dialog box
            title="Login History",
            text=history_text,
            buttons=[
                MDRaisedButton(text="Close", on_release=lambda x: self.dialog.dismiss())
            ],
        )
        self.dialog.open()

    # mini calendar
    def open_calendar(self):
        manager = RewardsManager(self.user_email)
        history = set(manager.data.get("login_history", []))  # gets log in history from the database

        # grid layout
        content = GridLayout(cols=7, rows=5, padding=dp(5), spacing=dp(5), size_hint=(None, None),
                             size=(dp(320), dp(280)))

        # labels for the days of the month (1 to 31)
        for i in range(1, 32):
            day = f"{i:02d}-{datetime.now().month:02d}-{datetime.now().year}"
            label = Label(
                text=str(i),
                color=(1, 0, 0, 1) if day in history else (0.4, 0.4, 0.4, 1),  # highlight login days in red
                font_size="16sp",
                size_hint=(None, None),
                size=(dp(40), dp(40)),
                halign="center",
                valign="middle",
            )
            content.add_widget(label)

        # dialog with size and padding
        self.calendar_dialog = MDDialog(
            title="Login Calendar",
            type="custom",
            content_cls=content,
            size_hint=(None, None),
            size=(dp(340), dp(340)),  # dialog to fit numbers
            buttons=[
                MDRaisedButton(text="Close", on_release=lambda x: self.calendar_dialog.dismiss())
            ]
        )
        self.calendar_dialog.open()



# Chat Bot Screen
# Author: Bogdan Postolachi

# Chose to use a .env file (environment variable) for better security and is a standard
# Source: https://www.datacamp.com/tutorial/python-environment-variables
# Source: https://blog.devgenius.io/why-a-env-7b4a79ba689
# Loads environment variable
# Loads the .env file which stores the API Key
load_dotenv(dotenv_path="chatbot_api.env")  # specifies the .env file to access

# Gets API Key from .env file
API_KEY = os.getenv("OPENAI_API_KEY")

# Error message in case API Key can't be accesed
if not API_KEY:
    print("Error: API Key not found")
    sys.exit(
        1)  #Stops the program, exit(1) indicates an error happened(Source: https://stackoverflow.com/questions/9426045/difference-between-exit0-and-exit1-in-python)

class ChatbotScreen(MDScreen):

    # constructor
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = openai.OpenAI(api_key=API_KEY)
        self.user_email = None
        self.chat_history = []  # initialize chat history list

    # method to be called from LoginScreen to set the user
    def set_user(self, email):
        self.user_email = email
        self.chat_history = self.load_chat_history()  # loads chat history from MongoDB

    # function to write logs
    # user_input - user messages
    # chat_response - bot responses
    def log_chat(self, user_input, chat_response):
        # Chat logging using MongoDB instead of text file
        # Each log contains user_email, timestamp, user message, and bot response
        # Source for Mongo insert: https://www.mongodb.com/docs/manual/tutorial/insert-documents/
        chat_document = {
            "user_email": self.user_email,
            "timestamp": datetime.now(),
            "user_input": user_input,
            "chat_response": chat_response
        }

        # Inserts the chat into MongoDB
        chat_collection.insert_one(chat_document)

    def load_chat_history(self):
        # Loads past chat history from MongoDB
        self.chat_history = []

        # MongoDB query to get all messages for current user, sorted by timestamp
        # Replaces old file-based loading logic
        logs = chat_collection.find(
            {"user_email": self.user_email}
        ).sort("timestamp", 1)

        # Parse logs into chat history in OpenAI format
        for log in logs:
            self.chat_history.append({"role": "user", "content": log["user_input"]})
            self.chat_history.append({"role": "assistant", "content": log["chat_response"]})

        return self.chat_history

    # code form the open AI platform was used for this method: https://platform.openai.com/docs/quickstart?api-mode=responses
    def chat_gpt(self, prompt):
        try:
            self.chat_history.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # specifying the chatgpt model

                # Specifying to the bot that it can only talk about mental health
                # Source: https://ihsavru.medium.com/how-to-build-your-own-custom-chatgpt-using-python-openai-78e470d1540e
                messages=[{"role": "system",
                           "content": "You are a mental health advisor. Your role is to help users dealing with mental health issues and provide support. All of your responses should be concise"}]
                         + self.chat_history[-10:],  # keep the last 10 messages
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

    # method to get user message and send it to chatgpt
    def send_message(self):
        try:
            # gets the text from the MDTextField
            user_input = self.ids.user_input.text.strip()  # removes white space

            # error message in case user presses send button without typing anything
            if not user_input:
                print("Warning: User input is empty, ignoring send request.")
                return

            bot_response = self.chat_gpt(user_input)

            # display user and bot messages
            self.display_message("You", user_input, align="right")
            self.display_message("Zen Bot", bot_response, align="left")

            self.ids.user_input.text = ""  # clears text field

        # in case any errors occur, like connection problems
        except Exception as e:
            print(f"ERROR in send_message: {e}")

    # function will display the messages
    def display_message(self, sender, message, align="left"):
        chat_box = self.ids.chat_box

        # label to store the messages
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

        # function is used to properly size and position a new chat message
        def finalize_layout(_):
            label.height = label.texture_size[1] + 20  # calculates the height of the label based on text
            label.width = label.texture_size[0]  # sets width of the label based on the text

            container = BoxLayout(
                size_hint_y=None,
                height=label.height + 20,
                orientation="horizontal",
                padding=[10, 5],
            )

            if align == "right":  # adds empty Widget() as a spacer then the label to push it to the right
                container.add_widget(Widget())
                container.add_widget(label)
            else:  # label is added first and the spacer comes after to push the message to the left
                container.add_widget(label)
                container.add_widget(Widget())

            chat_box.add_widget(container)
            chat_box.height += container.height + 10
            self.ids.chat_scroll.scroll_y = 0

        # delay to let Kivy calculate texture_size first
        Clock.schedule_once(finalize_layout, 0)



# Journal Screen
# Author: Damien Ho

class JournalScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.entries = []  # Holds all journal entries (active and archived)
        self.archive_view = False  # Viewing archived entries
        self.user_email = None  # Stores logged-in user's email

    def set_user(self, user_email):
        # assign the logged-in user's email and load their journal entries.
        self.user_email = user_email
        self.load_entries()

    def load_entries(self):
        # Load journal entries for the logged-in user.
        if not self.user_email:
            return
        self.entries = list(journals_collection.find({"user_email": self.user_email}))
        self.update_rv_data()

    def save_entries(self):
        # Save all journal entries to the database for the current user
        if not self.user_email:
            return
        for entry in self.entries:
            journals_collection.update_one({"_id": entry["_id"]}, {"$set": entry}, upsert=True)

    def update_rv_data(self):
        # Update the RecycleView with active or archived journal entries.
        if self.archive_view:
            data = [e for e in self.entries if e.get("archived", False)]
            self.ids.archive_label.opacity = 1 if not data else 0
        else:
            data = [e for e in self.entries if not e.get("archived", False)]
            self.ids.archive_label.opacity = 0
        self.ids.rv.data = [{"entry_id": str(e["_id"]), "text": e["text"], "date": e["date"]} for e in data]

    def add_entry(self):
        # Add a new journal entry for the logged-in user.
        entry_text = self.ids.entry_text.text.strip()
        if entry_text and self.user_email:
            new_entry = {
                "_id": str(uuid.uuid4()),
                "user_email": self.user_email,
                "text": entry_text,
                "date": datetime.now().strftime("%b %d, %Y • %I:%M %p"),
                "archived": False,
            }
            self.entries.append(new_entry)
            journals_collection.insert_one(new_entry)  # Save to DB
            self.update_rv_data()
            self.ids.entry_text.text = ""

    def remove_entry(self, entry_id):
        # Remove a journal entry.
        self.entries = [e for e in self.entries if str(e["_id"]) != entry_id]
        journals_collection.delete_one({"_id": entry_id})
        self.update_rv_data()

    def archive_entry(self, entry_id):
        # Archive a journal entry
        for entry in self.entries:
            if str(entry["_id"]) == entry_id:
                entry["archived"] = True
                # Set/update the  archived entry's archived boolean variable to true
                journals_collection.update_one({"_id": entry_id}, {"$set": {"archived": True}})
                break
        self.update_rv_data()

    def toggle_archive_view(self):
        # Switch between active and archived journal views
        self.archive_view = not self.archive_view
        self.ids.toggle_archive_btn.text = "Back to Journal" if self.archive_view else "View Archive"
        self.update_rv_data()

    def open_entry_dialog(self, entry_id):
        # Open a dialog to view and edit a journal entry.
        entry_to_edit = next((e for e in self.entries if str(e["_id"]) == entry_id), None)
        if not entry_to_edit:
            return

        container = MDBoxLayout(orientation="vertical", size_hint_y=None, height="300dp")
        scroll = ScrollView()
        text_field = MDTextField(text=entry_to_edit["text"], multiline=True, size_hint_y=None, height="300dp")
        scroll.add_widget(text_field)
        container.add_widget(scroll)

        def on_save(instance):
            entry_to_edit["text"] = text_field.text
            # update the user's journal data in mongoDB with the new entry
            journals_collection.update_one({"_id": entry_id}, {"$set": {"text": text_field.text}})
            self.update_rv_data()
            dialog.dismiss()

        def on_cancel(instance):
            dialog.dismiss()

        dialog = MDDialog(
            title="View / Edit Entry",
            type="custom",
            content_cls=container,
            buttons=[
                MDFlatButton(text="Cancel", on_release=on_cancel),
                MDFlatButton(text="Save", on_release=on_save),
            ]
        )
        dialog.open()


# Settings Screen
# Author: Connor Reid
class SettingsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dark_mode = BooleanProperty(True)
        self.notifications_enabled = BooleanProperty(True)
        self.theme_colors = ["Blue", "Red", "Green", "Purple", "Indigo"]
        self.current_theme_index = 0
        self.theme_cls = MDApp.get_running_app().theme_cls  # Get theme class from MDApp
        self.theme_cls.theme_style = "Light"  # Set the initial theme style

    # Toggles dark mode
    def toggle_dark_mode(self, instance, value):

        self.dark_mode = value

        self.update_theme()

    # Toggles Notifications
    def toggle_notifications(self, instance, value):

        self.notifications_enabled = value

    def change_theme(self):

        self.current_theme_index = (self.current_theme_index + 1) % len(self.theme_colors)

        self.theme_cls.primary_palette = self.theme_colors[self.current_theme_index]

        self.update_theme()

    # Updates through different themes
    def update_theme(self):

        if self.dark_mode:

            self.theme_cls.theme_style = "Dark"

            Window.clearcolor = (0.1, 0.1, 0.1, 1)

        else:

            self.theme_cls.theme_style = "Light"

            Window.clearcolor = (1, 1, 1, 1)


# Habit Input Dialog for adding habits
class HabitInputDialog(MDBoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.orientation = "vertical"

        self.spacing = "10dp"

        self.padding = "10dp"

        self.habit_input = MDTextField(

            hint_text="Enter habit",

            size_hint_y=None,

            height="48dp",

        )

        self.add_widget(self.habit_input)


# Habit Tracker Screen
# Author: Connor Reid
class HabitTrackerScreen(MDScreen):
    # Class constructor
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_days = []
        self.user_email = None  # Stores logged-in user
        self.habits = {}  # Store habits categorized by days
        self.dialog = None

    def set_user(self, user_email):
        # Assigns the logged-in user and loads their habits.
        self.user_email = user_email
        self.load_habits()

    def load_habits(self):
        # Loads the user's habits from MongoDB.

        if not self.user_email:
            # Exit if no user is logged in
            return

        # Query the database for all habits associated with the logged-in user
        user_habits = list(habits_collection.find({"user_email": self.user_email}))

        # Initialize an empty dictionary to store habits by day
        self.habits = {}

        # Loop through each habit entry returned from MongoDB
        for habit in user_habits:
            day = habit["day"]
            if day not in self.habits:
                # Create a new list for the day if it doesn't exist
                self.habits[day] = []

            # Append the habit name to the corresponding day
            self.habits[day].append(habit["habit_name"])

        # apply any day filtering logic to the loaded habits (e.g., based on selected day)
        self.filter_habits()

    #saves habits to MongoDB.
    def save_habits(self):
        # if no user email is retrieved from the login screen
        if not self.user_email:
            # return (no user logged in, no save)
            return

        # delete all existing habits for this user to avoid duplicates
        habits_collection.delete_many({"user_email": self.user_email})

        # iinsert each habit entry per day back into the database
        for day, habits in self.habits.items():
            for habit in habits:
                habits_collection.insert_one({
                    "_id": str(uuid.uuid4()),  # generate a unique ID for each habit entry
                    "user_email": self.user_email,
                    "habit_name": habit,
                    "day": day,
                })

    # Toggles selected day and updates habit list
    def toggle_day_selection(self, button):
        day = button.text
        if day in self.selected_days:
            self.selected_days.remove(day)
            button.md_bg_color = [0.6, 0.6, 0.6, 1]
        else:
            self.selected_days.append(day)
            button.md_bg_color = [0, 0, 0, 0]
        self.filter_habits()

    def add_habit_dialog(self):
        if not self.dialog:
            self.dialog_content = MDTextField(hint_text="Enter habit name")
            self.dialog = MDDialog(
                title="Add Habit",
                type="custom",
                content_cls=self.dialog_content,
                buttons=[
                    MDFlatButton(text="Cancel", on_release=lambda x: self.dialog.dismiss()),
                    MDFlatButton(text="Add", on_release=lambda x: self.add_habit(self.dialog_content.text)),
                ],
            )
        self.dialog.open()

    def add_habit(self, habit_name):
        habit_name = habit_name.strip()
        if not habit_name or not self.selected_days:
            return

        for day in self.selected_days:
            if day not in self.habits:
                self.habits[day] = []
            if habit_name not in self.habits[day]:
                self.habits[day].append(habit_name)

        self.save_habits()
        self.dialog.dismiss()
        self.filter_habits()

    def add_habit_card(self, habit_name, day):
        for card in self.ids.habits_list.children:
            if hasattr(card, "habit_name") and card.habit_name == habit_name:
                return

        card = MDCard(
            orientation="vertical",
            size_hint=(0.9, None),
            height="115dp",
            pos_hint={"center_x": 0.5},
            elevation=10,
            padding="10dp",
        )
        card.habit_name = habit_name

        label = MDLabel(text=habit_name, halign="center")
        delete_button = MDIconButton(
            icon="trash-can",
            on_release=lambda x: self.delete_habit(habit_name, day, card)
        )

        card.add_widget(label)
        card.add_widget(delete_button)
        self.ids.habits_list.add_widget(card)
        self.ids.habits_list.height += card.height

    def delete_habit(self, habit_name, day, card):
        if day in self.habits and habit_name in self.habits[day]:
            self.habits[day].remove(habit_name)
            if not self.habits[day]:
                del self.habits[day]
            self.ids.habits_list.remove_widget(card)
            self.save_habits()

    def filter_habits(self):
        self.ids.habits_list.clear_widgets()
        unique_habits = set()

        for day in self.selected_days:
            if day in self.habits:
                for habit in self.habits[day]:
                    if habit not in unique_habits:
                        unique_habits.add(habit)
                        self.add_habit_card(habit, day)

        self.ids.habits_list.height = len(unique_habits) * 120


# Meditation Screen
# Author: Damien Ho
class MeditationScreen(MDScreen):
    time_left = NumericProperty(0)  # Updates UI automatically
    timer_label_text = StringProperty(
        "00:00")  # The timer display in sync. This property type can store a string that updates text based UI elements like 'MDLabel'

    # Constructor for MeditationScreen
    def __init__(self,
                 **kwargs):  # **kwargs allows passing additional arguments if you don't know how many, Source: https://www.w3schools.com/python/gloss_python_function_arbitrary_keyword_arguments.asp
        super().__init__(**kwargs)  # Calls the parent class constructor (Screen)
        self.timer = None  # Stores the clock event for the timer
        self.current_sound = None  # Initialized variable to store the currently playing sound
        self.selected_sound_path = None  # Initialized variable to store the file path of selected meditation sound, e.g.,"sounds/Ocean.mp3".
        self.alarm_sound = None

    def start_timer(self):
        if self.timer: return  # Timer already running

        self.time_left = self.time_left or 600  # Default to 10 minutes if not set
        self.update_timer_label()

        self.stop_sound()  # Stops currently playing sound

        # Set default sound if there is no selected sound
        self.selected_sound_path = self.selected_sound_path or os.path.join(SOUNDS_FOLDER, "Default.mp3")
        self.play_sound(repeat=True)  # Setting it as True allows to play sound in a loop
        self.timer = Clock.schedule_interval(self.update_time, 1)

    def update_time(self, dt):
        if self.time_left > 0:
            self.time_left -= 1  # Decreasing time left by 1 second
            self.update_timer_label()  # Updates UI dynamically
        elif self.time_left == 0 and self.timer:  # Ensures this runs only when timer was running
            self.cancel_timer()  # stops the timer
            self.stop_sound()  # stops the meditation sound
            self.show_end_message()  # Pop-up and play end sound

    def update_timer_label(self):
        self.timer_label_text = f"{self.time_left // 60:02}:{self.time_left % 60:02}"
        if 'timer_label' in self.ids:
            self.ids.timer_label.text = self.timer_label_text

    def show_end_message(self):
        self.play_end_sound()

        # Close button for the dialog
        close_button = MDFlatButton(
            text="OK",
            on_release=lambda x: self.dismiss_message(),  # Dismiss pop-up when OK is clicked
            md_bg_color=(0.2, 0.6, 0.8, 1),  # color for the button
            text_color=(1, 1, 1, 1)  # text color
        )

        # Create the dialog pop-up
        self.end_dialog = MDDialog(
            title="Time's Up!",
            text="Meditation complete. You may continue or reset the session.",
            buttons=[close_button],
            radius=[20, 20, 20, 20],  # round corners
            auto_dismiss=False,
        )

        # Show the popup dialog
        self.end_dialog.open()

    # Stops the alarm sound
    def dismiss_message(self):
        if self.alarm_sound:  # Stops alarm if it's playing
            self.alarm_sound.stop()
            self.alarm_sound = None  # reset

        if self.end_dialog:
            self.end_dialog.dismiss()  # clos the pop-up

    def play_end_sound(self):
        end_sound_path = os.path.join(SOUNDS_FOLDER, "alarm.mp3")
        self.alarm_sound = SoundLoader.load(end_sound_path)  # Stores the instance in self.alarm_sound

        if self.alarm_sound:
            self.alarm_sound.play()  # Plays the end sound

    def pause_timer(self):
        self.cancel_timer()
        self.stop_sound()

    def reset_timer(self):
        self.cancel_timer()  # Ensure the timer is stopped
        self.stop_sound()
        self.time_left = 0
        self.timer_label_text = "00:00"  # Set text manually to prevent triggering update_time()

        if 'timer_label' in self.ids:
            self.ids.timer_label.text = self.timer_label_text

    def select_sound(self, sound_filename):
        self.stop_sound()  # Stop any currently playing sound
        self.selected_sound_path = os.path.join(SOUNDS_FOLDER, sound_filename)
        self.play_sound(repeat=False)  # Setting it as False only plays once
        Clock.schedule_once(lambda dt: self.stop_sound(), 5)  # Play snippet for 5 sec because

        if self.timer:  # If the timer is running, restart the selected sound in a loop after the snippet
            Clock.schedule_once(lambda dt: self.play_sound(repeat=True), 5)  # Resume after 5 sec

    def play_sound(self, repeat=False):
        self.stop_sound()  # Stop any existing playing sound
        self.current_sound = SoundLoader.load(
            self.selected_sound_path)  # Load selected sound file into self.current_sound.
        if self.current_sound:  # Check if the sound was loaded.
            self.current_sound.repeat = repeat  # Enables looping if it's required
            self.current_sound.play()  # Play the sound

    def stop_sound(self):
        if self.current_sound:
            self.current_sound.stop()  # Stops playback when calling the built-in stop() method.
            self.current_sound = None  # Reset the current_sound to none so the system knows no sound is currently active

    def cancel_timer(self):
        if self.timer:
            self.timer.cancel()  # Using the .cancel built in property allows repeated calls being stopped.
            self.timer = None

    def on_leave(self):
        self.cancel_timer()  # Stop the timer
        self.stop_sound()  # Stop any playing sound


# Mood Tracker
# Author: Soheib Ameur
class MoodTrackerScreen(MDScreen):
    # class constructor
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_id = None  # Initialize user_id to None

    # this function will be call in the MainApp on_start method to load the logged-in user's week data into the spinner
    def on_load(self):
        if not self.user_id:
            print("User ID is not set!")
            return

        # Fetch and load only the logged-in user's mood data
        user_mood_data = mood_collection.find({"user_id": ObjectId(self.user_id)})
        mood_data = {entry["week_key"]: entry["mood_data"] for entry in user_mood_data}

        # Sort the available weeks data
        available_weeks = sorted(mood_data.keys())
        # if there is data in the available weeks dictionary
        if available_weeks:
            # add the values from the available weeks to the spinner
            self.ids.week_spinner.values = available_weeks
            # Plot the latest week data
            self.plot_graph(available_weeks[-1])

        # Check and show daily popup
        self.show_popup()

    def show_popup(self):
        # get the today's date in this format "Year-Month-Day"
        today = datetime.today().strftime("%Y-%m-%d")

        # Check if the user has already logged in today
        existing_entry = popup_collection.find_one({
            "user_id": ObjectId(self.user_id),
            "date": today
        })

        # If the pop for today exists
        if existing_entry:
            # return
            print("User has already seen the popup today.")
            return

        # Create a BoxLayout layout
        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        # Create a label for the above layout
        label = Label(text="How are you feeling today?", font_size=20, color=(1, 1, 1, 1))
        # add the label to the layout
        layout.add_widget(label)

        # create a layout for the icon_layout
        icon_layout = BoxLayout(orientation="horizontal", spacing=15)

        # create an emotions dictionary for the icons .png and mood
        emotions = {
            "crying.png": 1,  # Very sad
            "sad.png": 2,  # Sad
            "confused.png": 3,  # Neutral
            "happy.png": 4,  # Happy
            "happy-face.png": 5  # Very happy
        }

        # for each icon and mood value pair in the emotions dictionary
        for icon, mood_value in emotions.items():
            # Create a button with that icon
            button = MDIconButton(icon=icon)
            # And bind the icon_click function to that icon with that icons mood value
            button.bind(on_release=lambda instance, value=mood_value: self.icon_click(instance, value))
            # add the button the icon layout
            icon_layout.add_widget(button)

        # Add the icon layout to the
        layout.add_widget(icon_layout)

        # Create popup and add the layout created above as it's content
        self.popup = Popup(
            title="Mood PopUp",
            content=layout,
            size_hint=(1, 0.4),
            auto_dismiss=True,
            background_color=(0, 0, 0, 1)
        )
        # show the popup
        self.popup.open()

        # Store in MongoDB that the user has seen the popup today
        popup_collection.insert_one({"user_id": ObjectId(self.user_id), "date": today})

    def store_mood_data(self, week_key, mood_data):
        if not self.user_id:
            print("User ID is not set, cannot store mood data!")
            return

        # update
        mood_collection.update_one(
            {"user_id": ObjectId(self.user_id), "week_key": week_key},
            {"$set": {"mood_data": mood_data}},
            upsert=True
        )

    def icon_click(self, instance, mood_value):
        today = datetime.today()
        week_key = today.strftime("%Y-W%U")
        day_number = today.isoweekday()

        # Retrieve the user's existing mood data for this week
        mood_entry = mood_collection.find_one({
            "user_id": ObjectId(self.user_id),
            "week_key": week_key
        })

        # If no entry exists, create an empty mood data dictionary
        mood_data = mood_entry["mood_data"] if mood_entry else {}

        # Update mood data for the selected day
        mood_data[str(day_number)] = mood_value

        # Store the updated mood data in MongoDB
        self.store_mood_data(week_key, mood_data)

        print(f"Stored mood {mood_value} for {week_key}, Day {day_number}")
        # Hide the pop-up
        self.popup.dismiss()

        # call the on_load method to refresh screen with updated data
        self.on_load()

    # Function for plotting the graph
    def plot_graph(self, selected_week):
        # if the user id is not retrieved from the login
        if not self.user_id:
            # The graph can't be plotted
            print("User ID is not set, cannot plot graph!")
            return

        # Map numbers with day values for later use
        day_mapping = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat", 7: "Sun"}

        # Find the user's mood data for the selected week in the mood_collection collection from mongoDb
        mood_entry = mood_collection.find_one({
            "user_id": ObjectId(self.user_id),
            "week_key": selected_week
        })

        # If there is no data in the selected week
        if not mood_entry or "mood_data" not in mood_entry:
            # print that there is not data for the selected week
            print(f"No data available for {selected_week}")
            return

        # Get mood values and corresponding days
        days = sorted(mood_entry["mood_data"].keys(), key=int)
        moods = [mood_entry["mood_data"][day] for day in days]
        day_labels = [day_mapping[int(day)] for day in days]

        # Plot the mood data
        fig, ax = plt.subplots()
        # Plot the day labels on the y-axis, and the mood data on the x-axis
        ax.plot(day_labels, moods, marker="o", linestyle="-", color="green", linewidth=2)
        # Label the x-axis
        ax.set_xlabel("Days")
        # Label the y-axis
        ax.set_ylabel("Mood")
        # Give the graph a title
        ax.set_title(f"Mood Tracker - {selected_week}")
        ax.grid(True)

        # Update the graph in mood screen
        graph_container = self.ids.graph_container
        graph_container.clear_widgets()
        graph_container.add_widget(FigureCanvasKivyAgg(fig))

    # def clearGraph(self):
    #     graph = self.root.ids.graph
    #
    #     for x in graph.plots[:]:
    #         graph.remove_plot(x)


# Reset Screen
# Author: Soheib Ameur
class ResetScreen(MDScreen):
    # Class Constructor
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_email = None  # Store email from ForgotScreen

    # Function to reset the password
    def reset_password(self):
        # Get the new password input from the user
        new_password = self.ids.new_password.text.strip()
        confirm_password = self.ids.confirm_password.text.strip()

        # If one or more of the fields is empty
        if not new_password or not confirm_password:
            # Inform the user
            toast("Please enter both password fields!")
            return

        # If the new password and the confirm password fields don't have the same values
        if new_password != confirm_password:
            # Inform the user
            toast("Passwords do not match!")
            return

        # If the password is not logn enough
        if len(new_password) < 8:
            toast("Password too short! Must be at least 8 characters.")
            return

        # Update password in mongoDB
        result = users_collection.update_one(
            {"email": self.user_email},
            {"$set": {"password": new_password}}
        )

        # If theere has been a modification, meaning the update was successful
        if result.modified_count > 0:
            # Inform the user
            toast("Password reset successful! Please log in.")
            # and switch to the login_screen
            self.manager.current = "login_screen"
        else:
            # If not, then inform the user that there has been an error
            toast("Error updating password. Try again.")


# Login Screen
# Author: Soheib Ameur
class LoginScreen(MDScreen):
    def login_btn(self):
        email = self.ids.email.text.strip()
        password = self.ids.password.text.strip()

        if not email or not password:
            print("Please fill in all fields.")
            toast("Please fill in all fields.")
            return

        # Query  mongoDB for finding the user
        user = users_collection.find_one({"email": email, "password": password})

        # If the user is found
        if user:
            # inform the user of a successful login
            toast("Login Successful", background=[0.2, 1, 0.2, 1])
            print("Login Successful")

            # Get the user's objectId
            user_id = str(user["_id"])
            print(f"Logged in user ID: {user_id}")

            self.ids.email.text = ""
            self.ids.password.text = ""

            # get the current running app
            app = MDApp.get_running_app()

            # Change screen to the mood screen
            app.root.ids.sm.current = "mood_screen"

            # Access the all the screens through the screen manager
            journal_screen = app.root.ids.sm.get_screen("journal")
            rewards_screen = app.root.ids.sm.get_screen("rewards")
            habit_screen = app.root.ids.sm.get_screen("habits")
            chatbot_screen = app.root.ids.sm.get_screen("chatbot")
            mood_tracker_screen = app.root.ids.sm.get_screen("mood_screen")

            # set the logged-in user's email in all the screens
            journal_screen.set_user(email)
            habit_screen.set_user(email)
            chatbot_screen.set_user(email)
            rewards_screen.set_user(email)

            # pass user_id to mood screen and load their data
            mood_tracker_screen.user_id = user_id

            # call the on-load function from the mood tracker screen
            mood_tracker_screen.on_load()
            return
        else:
            toast("Invalid login details.", background=[0.8, 0, 0, 0.5])

# Forgot Screen
# Author: Soheib Ameur
class ForgotScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # verify the user's security answer
    def verify_security(self):
        #
        email = self.ids.f_email.text.strip()
        security_ans = self.ids.f_security.text.strip()

        if not email or not security_ans:
            toast("Please fill in all fields!")
            return

        user = users_collection.find_one({"email": email, "security_ans": security_ans})

        if user:
            toast("Verification successful!")
            reset_screen = self.manager.get_screen("reset_screen")
            reset_screen.user_email = email  # Store email for reset
            self.manager.current = "reset_screen"
        else:
            toast("Incorrect details! Try again.")


# Signup Screen
# Author: Soheib Ameur
class SignupScreen(MDScreen):
    def up_btn(self):
        email = self.ids.up_email.text.strip()
        password = self.ids.up_password.text.strip()
        fname = self.ids.fname.text.strip()
        lname = self.ids.lname.text.strip()
        security_ans = self.ids.security_ans.text.strip()

        # If any of the fields are empty
        if not email or not password or not fname or not lname or not security_ans:
            # Inform the user
            print("Please fill in all fields.")
            toast("Please fill in all fields.", duration=2)
            return

        # Checks if the length of the password entered is more than eight characters
        if len(password) < 8:
            # Inform the user
            print("Password too short! Must be at least 8 characters.")
            toast("Password too short! \nMust be at least 8 characters.", duration=2)
            return

        # Insert the user data into MongoDB
        users_collection.insert_one({
            "email": email,
            "password": password,
            "fname": fname,
            "lname": lname,
            "security_ans": security_ans
        })
        # Display a success message on screen
        toast("Successfully Signed Up!")
        self.ids.up_email.text = ""
        self.ids.up_password.text = ""


# Main app class
# Team effort
class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        root = Builder.load_file("main.kv")
        return root

    # Can be bound to a button to change on other screens to return to the login_screen
    def goto_login(self):
        print("Login button clicked")
        self.root.ids.sm.current = "login_screen"

    # Built-in function that is called once the app is started
    def on_start(self):
        mood_tracker_screen = self.root.ids.sm.get_screen("mood_screen")
        mood_tracker_screen.on_load()


# Create an instance of the MainApp class
main_app = MainApp()

# Run that instance of the main app class
main_app.run()
