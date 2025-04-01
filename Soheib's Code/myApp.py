from pymongo import MongoClient
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.uix.button import MDIconButton
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivy.uix.popup import Popup
from kivy.uix.label import Label
import datetime
from kivy_garden.matplotlib import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
from kivymd.toast import toast
from kivymd.uix.screen import MDScreen
from kivy.uix.spinner import SpinnerOption
from bson import ObjectId
import os
from kivy.uix.screenmanager import Screen
import json
import uuid
from kivy.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton



Window.size = (400, 720)

client = MongoClient("mongodb://127.0.0.1:27017/")
db = client["Kivy_app"]
users_collection = db["users"]
mood_collection = db["mood_data"]
popup_collection = db["daily_popup"]


class CustomSpinnerOption(SpinnerOption):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0.2, 0, 1)
        self.color = (1, 1, 1, 1)
        self.font_size = "16sp"
        self.height = 40


JOURNAL_FILE = "journal.json"


# class JournalScreen(Screen):
#     def __init__(self, **kwargs):
#         """Initializes the journal screen and loads saved entries from file."""
#         super().__init__(**kwargs)
#         self.entries = []  # Holds all journal entries (active and archived)
#         self.archive_view = False  # viewing archived entries
#         self.load_entries()  # Load existing entries on start
#
#     def on_kv_post(self, base_widget):
#         # update the list view after the UI is loaded.
#         self.update_rv_data()
#
#     def load_entries(self):
#         # load journal entries from a JSON file if it exist
#         if os.path.exists(JOURNAL_FILE):
#             with open(JOURNAL_FILE, "r") as f:
#                 self.entries = json.load(f)
#         else:
#             self.entries = []  # fallback: start with empty list
#
#     def save_entries(self):
#         # Save current list of entries to a JSON file
#         with open(JOURNAL_FILE, "w") as f:
#             json.dump(self.entries, f)
#
#     def update_rv_data(self):
#         # update the list view data based on whether archived entries are shown
#         if self.archive_view:
#             # filtering archived entries only
#             data = [e for e in self.entries if e.get("archived", False)]
#             self.ids.archive_label.opacity = 1 if not data else 0  # show message if no archived entries
#         else:
#             # flitering active entries only
#             data = [e for e in self.entries if not e.get("archived", False)]
#             self.ids.archive_label.opacity = 0  # hide label in active mode
#
#         self.ids.rv.data = data  # update the RecycleView's data
#
#     def add_entry(self):
#         """Adds a new journal entry from the text input. Uses .strip() to prevent blank entries with only whitespace."""
#         entry_text = self.ids.entry_text.text
#         if entry_text.strip():  # using .strip() to check for non-empty text
#             new_entry = {
#                 "entry_id": str(uuid.uuid4()),  # generate a unique ID for the entry
#                 "text": entry_text,
#                 "date": datetime.datetime.now().strftime("%b %d, %Y • %I:%M %p"),
#                 "archived": False,  # default is active, not archived
#             }
#             self.entries.append(new_entry)  # append new enetry to the list
#             self.save_entries()  # write changes to file
#             self.update_rv_data()  # refresh the RecycleView
#             self.ids.entry_text.text = ""  # clear text input
#
#     def remove_entry(self, entry_id):
#         """Deletes a journal entry using its unique ID. Uses a list comprehension to filter out the matching entry."""
#         self.entries = [e for e in self.entries if e["entry_id"] != entry_id]  # remove the entry
#         self.save_entries()
#         self.update_rv_data()
#
#     def archive_entry(self, entry_id):
#         """Marks an entry as archived so it no longer shows in active view.Looping through entries to find a match by ID."""
#         for e in self.entries:  # looping through all entries
#             if e["entry_id"] == entry_id:
#                 e["archived"] = True  # set as archived
#                 break
#         self.save_entries()
#         self.update_rv_data()
#
#     def toggle_archive_view(self):
#         """Switches between viewing active and archived entries.Also updates the button label accordingly."""
#         self.archive_view = not self.archive_view  # Flip the view mode
#         self.ids.toggle_archive_btn.text = (
#             "Back to Journal" if self.archive_view else "View Archive"
#         )
#         self.update_rv_data()
#
#     def open_entry_dialog(self, entry_id):
#         """Opens a popup dialog to view/edit an entry’s text.Finds the entry using its unique ID."""
#         entry_to_edit = next((e for e in self.entries if e["entry_id"] == entry_id),
#                              None)  # find the entry with matching ID
#         if not entry_to_edit:
#             return  # entry not found, do nothing
#
#         # layout for the popup content
#         container = MDBoxLayout(orientation="vertical", size_hint_y=None, height="300dp")
#         scroll = ScrollView()
#         text_field = MDTextField(
#             text=entry_to_edit["text"],
#             multiline=True,
#             size_hint_y=None,
#             height="300dp"
#         )
#         scroll.add_widget(text_field)
#         container.add_widget(scroll)
#
#         # define save button action
#         def on_save(instance):
#             entry_to_edit["text"] = text_field.text  # update entry text
#             self.save_entries()  # save to file
#             self.update_rv_data()  # refresh entry list
#             dialog.dismiss()  # close the popup
#
#         # define cancel button action
#         def on_cancel(instance):
#             dialog.dismiss()
#
#         dialog = MDDialog(
#             title="View / Edit Entry",
#             type="custom",
#             content_cls=container,
#             buttons=[
#                 MDFlatButton(text="Cancel", on_release=on_cancel),
#                 MDFlatButton(text="Save", on_release=on_save)
#             ]
#         )
#         dialog.open()


class MoodTrackerScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_id = None  # Initialize user_id to None

    def on_load(self):
        if not self.user_id:
            print("User ID is not set!")
            return

        # Fetch and load only the logged-in user's mood data
        user_mood_data = mood_collection.find({"user_id": ObjectId(self.user_id)})
        mood_data = {entry["week_key"]: entry["mood_data"] for entry in user_mood_data}

        available_weeks = sorted(mood_data.keys())
        if available_weeks:
            self.ids.week_spinner.values = available_weeks
            self.plot_graph(available_weeks[-1])

        # Check and show daily popup
        self.show_popup()

    def show_popup(self):
        today = datetime.datetime.today().strftime("%Y-%m-%d")

        # Check if the user has already logged in today
        existing_entry = popup_collection.find_one({
            "user_id": ObjectId(self.user_id),
            "date": today
        })

        if existing_entry:
            print("User has already seen the popup today.")
            return

        # Create and display the popup
        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        label = Label(text="How are you feeling today?", font_size=20, color=(1, 1, 1, 1))
        layout.add_widget(label)

        icon_layout = BoxLayout(orientation="horizontal", spacing=15)
        emotions = {
            "crying.png": 1,  # Very sad
            "sad.png": 2,  # Sad
            "confused.png": 3,  # Neutral
            "happy.png": 4,  # Happy
            "happy-face.png": 5  # Very happy
        }

        for icon, mood_value in emotions.items():
            button = MDIconButton(icon=icon)
            button.bind(on_release=lambda instance, value=mood_value: self.icon_click(instance, value))
            icon_layout.add_widget(button)

        layout.add_widget(icon_layout)

        self.popup = Popup(
            title="Daily Reminder",
            content=layout,
            size_hint=(1, 0.4),
            auto_dismiss=True,
            background_color=(0, 0, 0, 1)
        )
        self.popup.open()

        # Store in MongoDB that the user has seen the popup today
        popup_collection.insert_one({"user_id": ObjectId(self.user_id), "date": today})

    def store_mood_data(self, week_key, mood_data):
        if not self.user_id:
            print("User ID is not set, cannot store mood data!")
            return

        mood_collection.update_one(
            {"user_id": ObjectId(self.user_id), "week_key": week_key},
            {"$set": {"mood_data": mood_data}},
            upsert=True
        )

    def icon_click(self, instance, mood_value):
        today = datetime.datetime.today()
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
        self.popup.dismiss()

        # Refresh screen with updated data
        self.on_load()

    def plot_graph(self, selected_week):
        if not self.user_id:
            print("User ID is not set, cannot plot graph!")
            return

        day_mapping = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat", 7: "Sun"}

        # Find the user's mood data for the selected week
        mood_entry = mood_collection.find_one({
            "user_id": ObjectId(self.user_id),
            "week_key": selected_week
        })

        if not mood_entry or "mood_data" not in mood_entry:
            print(f"No data available for {selected_week}")
            return

        #Get mood values and corresponding days
        days = sorted(mood_entry["mood_data"].keys(), key=int)
        moods = [mood_entry["mood_data"][day] for day in days]
        day_labels = [day_mapping[int(day)] for day in days]

        # Plot the mood data
        fig, ax = plt.subplots()
        ax.plot(day_labels, moods, marker="o", linestyle="-", color="green", linewidth=2)
        ax.set_xlabel("Days")
        ax.set_ylabel("Mood")
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


class ResetScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_email = None  # Store email from ForgotScreen

    def reset_password(self):
        new_password = self.ids.new_password.text.strip()
        confirm_password = self.ids.confirm_password.text.strip()

        if not new_password or not confirm_password:
            toast("Please enter both password fields!")
            return

        if new_password != confirm_password:
            toast("Passwords do not match!")
            return

        if len(new_password) < 8:
            toast("Password too short! Must be at least 8 characters.")
            return

        # Update password in mongoDB
        result = users_collection.update_one(
            {"email": self.user_email},
            {"$set": {"password": new_password}}
        )

        if result.modified_count > 0:
            toast("Password reset successful! Please log in.")
            self.manager.current = "login_screen"
        else:
            toast("Error updating password. Try again.")


class LoginScreen(MDScreen):
    def login_btn(self):
        email = self.ids.email.text.strip()
        password = self.ids.password.text.strip()

        if not email or not password:
            print("Please fill in both fields.")
            return

        # Query  mongoDB for finding the user
        user = users_collection.find_one({"email": email, "password": password})

        self.ids.email.text = ""
        self.ids.password.text = ""

        if user:
            toast("Login Successful", background=[0.2, 1, 0.2, 1])
            print("Login Successful")

            # Get the user's objectId
            user_id = str(user["_id"])
            print(f"Logged in user ID: {user_id}")

            app = MDApp.get_running_app()
            app.root.ids.sm.current = "mood_screen"

            # Pass user_id to MoodTrackerScreen and load their data
            mood_tracker_screen = app.root.ids.sm.get_screen("mood_screen")
            mood_tracker_screen.user_id = user_id
            mood_tracker_screen.on_load()
            return
        else:
            toast("Invalid login details.", background=[1, 0, 0, 0.5])

class ForgotScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def verify_security(self):
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


class SignupScreen(MDScreen):
    def up_btn(self):
        email = self.ids.up_email.text.strip()
        password = self.ids.up_password.text.strip()
        fname = self.ids.fname.text.strip()
        lname = self.ids.lname.text.strip()
        security_ans = self.ids.security_ans.text.strip()

        if not email or not password or not fname or not lname or not security_ans:
            print("Please fill in all fields.")
            return

        if len(password) < 8:
            print("Password too short! Must be at least 8 characters.")
            return

        # Insert the user data into MongoDB
        users_collection.insert_one({
            "email": email,
            "password": password,
            "fname": fname,
            "lname": lname,
            "security_ans": security_ans
        })

        toast("Successfully Signed Up!")
        self.ids.up_email.text = ""
        self.ids.up_password.text = ""

class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        root = Builder.load_file("main.kv")
        return root

    def goto_login(self):
        print("Login button clicked")
        self.root.ids.sm.current = "login_screen"

    def on_start(self):
        mood_tracker_screen = self.root.ids.sm.get_screen("mood_screen")
        mood_tracker_screen.on_load()


main_app = MainApp()
main_app.run()