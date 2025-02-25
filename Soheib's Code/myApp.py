import json
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.uix.button import MDIconButton
from kivy.uix.boxlayout import BoxLayout
import mysql.connector
from kivymd.app import MDApp
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.storage.jsonstore import JsonStore
from datetime import datetime
from kivy_garden.matplotlib import FigureCanvasKivyAgg
import matplotlib.pyplot as plt


Window.size = (400, 720)


mydb = mysql.connector.connect(
  host="127.0.0.1",
  user="root",
  password="PUT_PASSWORD_IN_HERE",
  database="python",
  auth_plugin="mysql_native_password"
)

mycursor = mydb.cursor()

sql_sign_up = "INSERT INTO python.users(email, password, fname, lname, security_ans) VALUES (%s, %s, %s, %s, %s)"
sql_sign_in = "SELECT * FROM python.users WHERE email=%s and  password= %s"

SOUNDS_FOLDER = "sounds_folder"


class myApp(MDApp):
    def build(self):
        self.store = JsonStore("daily_popup.json")
        return Builder.load_file("my.kv")

    def on_start(self):
        self.plot_graph()


    def show_popup(self):
        today = datetime.today().strftime("%Y-%m-%d")

        if not self.store.exists("last_shown") or self.store.get("last_shown")["date"] != today:
            layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

            label = Label(
                text="How are you feeling today?",
                font_size=20,
                color=(1, 1, 1, 1)
            )
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
            # Save today's date to prevent showing the popup again today
            self.store.put("last_shown", date=today)

    def icon_click(self, instance, mood_value):
        """Stores the selected mood into the JSON file based on the current day."""
        day_mapping = {
            "Monday": 1,
            "Tuesday": 2,
            "Wednesday": 3,
            "Thursday": 4,
            "Friday": 5,
            "Saturday": 6,
            "Sunday": 7
        }

        today_name = datetime.today().strftime("%A")  # Find out what today is i.e Monday
        day_number = day_mapping[today_name]  # Convert to a number (1-7)

        try:
            with open("data.json", "r") as f:
                mood_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            mood_data = {}

        mood_data[str(day_number)] = mood_value  # Store mood with the day number as the key

        with open("data.json", "w") as f:
            json.dump(mood_data, f, indent=4)  # Save back to the json file

        print(f"Stored mood {mood_value} for {today_name} (Day {day_number})")

        self.popup.dismiss()
        self.plot_graph()  # Update the graph after saving


    def login_btn(self):
        email = self.root.ids.email
        password = self.root.ids.password

        if email.text == "" or password.text == "":
            print("Please Fill in Both Fields")

        else:
            print("Email: ", email.text, "\nPassword:", password.text)
            values = (email.text, password.text)
            print(mycursor.execute(sql_sign_in, values))
            print("Successfully Signed Up")
            result = mycursor.fetchone()

            email.text = ""
            password.text = ""

            if result:
                print("Login Successful")
                self.root.ids.sm.current = "mood_screen"
                self.show_popup()
                email.text = ""
                password.text = ""
            else:
                print("Invalid Login Details")


    def up_btn(self):
        email = self.root.ids.up_email
        password = self.root.ids.up_password
        fname = self.root.ids.fname
        lname = self.root.ids.lname
        security_ans = self.root.ids.security_ans

        password_input = password.text

        if email.text == "" or password.text == "" or fname.text == "" or lname.text == "" or security_ans.text == "":
            print("Please Fill in All Fields")

        elif len(password_input) < 8:
            print("Password Too Short!")
            return

        else:
            print("Email: ", email.text, "\nPassword:", password.text)
            values = (email.text, password.text, fname.text, lname.text, security_ans.text)
            mycursor.execute(sql_sign_up, values)
            mydb.commit()
            print("Successfully Signed Up")
            email.text = ""
            password.text = ""
    def plot_graph(self):
        try:
            with open("data.json", "r") as f:
                mood_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            mood_data = {}

        day_mapping = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat", 7: "Sun"}

        # Sort data and get lists for plotting
        days = sorted(mood_data.keys(), key=int)
        moods = [mood_data[day] for day in days]

        # Convert day numbers to labels
        day_labels = [day_mapping[int(day)] for day in days]

        # Create figure
        fig, ax = plt.subplots()
        ax.plot(day_labels, moods, marker="o", linestyle="-", color="green", linewidth=2)

        # Set labels and grid
        ax.set_xlabel("Days")
        ax.set_ylabel("Mood")
        ax.set_title("Mood Tracker")
        ax.grid(True)

        # Clear previous graph and add new one
        graph_container = self.root.ids.graph_container
        graph_container.clear_widgets()
        graph_container.add_widget(FigureCanvasKivyAgg(fig))

    #graph.add_plot(plot)

    def clearGraph(self):
        graph = self.root.ids.graph

        for x in graph.plots[:]:
            graph.remove_plot(x)


app = myApp()
app.run()