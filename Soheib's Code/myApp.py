# Learned how to use mongodb with python using the following resouces: https://www.w3schools.com/python/python_mongodb_getstarted.asp, https://www.mongodb.com/docs/languages/python/pymongo-driver/current/
from pymongo import MongoClient
from kivymd.uix.button import MDIconButton
from kivy.uix.popup import Popup
# Learned how to use graphs with kivy using this video: https://youtu.be/83C4tl8scoY?si=JHFL_Gbi276w0nkE
from kivy_garden.matplotlib import FigureCanvasKivyAgg
from bson import ObjectId
import matplotlib.pyplot as plt
from kivy.uix.spinner import SpinnerOption

from kivy.uix.boxlayout import BoxLayout
from datetime import datetime
from kivymd.uix.screen import MDScreen
from kivy.core.window import Window
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.label import Label
from kivymd.toast import toast


Window.size = (400, 720)

client = MongoClient("mongodb://127.0.0.1:27017/")
db = client["Kivy_app"]
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


# Mood Tracker Screen
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


# Reset Password Screen
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
class LoginScreen(MDScreen):
    def login_btn(self):
        email = self.ids.email.text.strip()
        password = self.ids.password.text.strip()

        if not email or not password:
            print("Please fill in both fields.")
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
            # set the password and emails fields to being empty
            self.ids.email.text = ""
            self.ids.password.text = ""

            # get the current running app
            app = MDApp.get_running_app()

            # Access the mood screen through the screen manager
            app.root.ids.sm.current = "mood_screen"

            # Access the journal screen through the screen manager
            # journal_screen = app.root.ids.sm.get_screen("journal")

            # set the logged-in user's email in the journal screen
            # journal_screen.set_user(email)

            # Access the habits screen through the screen manager
            # habit_screen = app.root.ids.sm.get_screen("habits")

            # set the logged-in user's email in the habit screen
            # habit_screen.set_user(email)

            mood_tracker_screen = app.root.ids.sm.get_screen("mood_screen")
            # pass user_id to mood screen and load their data
            mood_tracker_screen.user_id = user_id

            # call the on-load function
            mood_tracker_screen.on_load()
            return
        else:
            toast("Invalid login details.", background=[1, 0, 0, 0.5])


# Forgot Password Screen
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