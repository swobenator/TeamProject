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
import datetime
from kivy_garden.matplotlib import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
from kivymd.toast import toast
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivy.uix.spinner import SpinnerOption

Window.size = (400, 720)

mydb = mysql.connector.connect(
  host="127.0.0.1",
  user="root",
  password="sweeb321",
  database="python",
  auth_plugin="mysql_native_password"
)

mycursor = mydb.cursor()

sql_sign_up = "INSERT INTO python.users(email, password, fname, lname, security_ans) VALUES (%s, %s, %s, %s, %s)"
sql_sign_in = "SELECT * FROM python.users WHERE email=%s and  password= %s"


class CustomSpinnerOption(SpinnerOption):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0.2, 0, 1)
        self.color = (1, 1, 1, 1)
        self.font_size = "16sp"
        self.height = 40


class MoodTrackerScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.store = JsonStore("daily_popup.json")

    def on_load(self):
        try:
            with open("data.json", "r") as f:
                mood_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            mood_data = {}

        available_weeks = sorted(mood_data.keys())  # Get all stored weeks

        if available_weeks:
            self.ids.week_spinner.values = available_weeks  # Update Spinner
            self.plot_graph(available_weeks[-1])

    def goto_login(self):
        self.root.ids.sm.current = "login_screen"

    def show_popup(self):

        today = datetime.datetime.today().strftime("%Y-%m-%d")

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

            self.store.put("last_shown", date=today)

    def icon_click(self, instance, mood_value):
        today = datetime.datetime.today()
        week_key = today.strftime("%Y-W%U")
        day_number = today.isoweekday()

        try:
            with open("data.json", "r") as f:
                mood_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            mood_data = {}

        if week_key not in mood_data:
            mood_data[week_key] = {}

        mood_data[week_key][str(day_number)] = mood_value  # Store mood

        with open("data.json", "w") as f:
            json.dump(mood_data, f, indent=4)

        available_weeks = sorted(mood_data.keys())

        print(f"Stored mood {mood_value} for {week_key}, Day {day_number}")
        self.popup.dismiss()
        if available_weeks:
            self.ids.week_spinner.values = available_weeks  # Update Spinner
            self.plot_graph(available_weeks[-1])

    def plot_graph(self, selected_week):

        try:
            with open("data.json", "r") as f:
                mood_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            mood_data = {}

        day_mapping = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat", 7: "Sun"}

        if selected_week not in mood_data:
            print(f"No data available for {selected_week}")
            return

        weekly_moods = mood_data[selected_week]

        days = sorted(weekly_moods.keys(), key=int)
        moods = [weekly_moods[day] for day in days]
        day_labels = [day_mapping[int(day)] for day in days]

        fig, ax = plt.subplots()
        ax.plot(day_labels, moods, marker="o", linestyle="-", color="green", linewidth=2)

        ax.set_xlabel("Days")
        ax.set_ylabel("Mood")
        ax.set_title(f"Mood Tracker - {selected_week}")
        ax.grid(True)

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

    def reset_password(self):
        new_password = self.ids.new_password.text.strip()
        confirm_password = self.ids.confirm_password.text.strip()

        if not new_password or not confirm_password:
            toast("Please enter both password fields!")
            return

        if new_password != confirm_password:
            toast("Passwords do not match!")
            return

        try:
            reset_screen = self.ids.sm.get_screen("reset_screen")
            email = reset_screen.user_email
            mycursor.execute("UPDATE users SET password = %s WHERE email = %s", (new_password, email))
            mydb.commit()
            toast("Password reset successful! Please log in.")
            self.root.ids.sm.current = "login_screen"

        except mysql.connector.Error as err:
            toast(f"Database Error: {err}")


class LoginScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def login_btn(self):
        email = self.ids.email
        password = self.ids.password

        if email == "" or password == "":
            print("Please Fill in Both Fields")

        else:
            values = (email.text.strip(), password.text.strip())
            print(mycursor.execute(sql_sign_in, values))

            result = mycursor.fetchone()

            email.text = ""
            password.text = ""

            if result:
                toast("Login Successful", background=[0.2, 1, 0.2, 1])

                app = MDApp.get_running_app()
                app.root.ids.sm.current = "mood_screen"

                mood_tracker_screen = app.root.ids.sm.get_screen("mood_screen")
                mood_tracker_screen.on_start()
                email.text = ""
                password.text = ""
            else:
                toast("Invalid Login Details", background=[1, 0, 0, 0.5])


class ForgotScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def verify_security(self):
        email = self.ids.f_email.text.strip()
        security_ans = self.ids.f_security.text.strip()

        if not email or not security_ans:
            toast("Please fill in all fields!")
            return

        try:
            mycursor.execute("SELECT * FROM users WHERE email = %s AND security_ans = %s", (email, security_ans))
            result = mycursor.fetchone()

            if result:
                toast("Verification successful!")
                reset_screen = self.ids.sm.get_screen("reset_screen")
                reset_screen.user_email = email
                self.ids.sm.current = "reset_screen"
            else:
                toast("Incorrect details! Try again.")

        except mysql.connector.Error as err:
            toast(f"Database Error: {err}")


class SignupScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def up_btn(self):
        email = self.ids.up_email
        password = self.ids.up_password
        fname = self.ids.fname
        lname = self.ids.lname
        security_ans = self.ids.security_ans

        # password_input = password.text.strip()

        if email.text == "" or password.text == "" or fname.text == "" or lname.text == "" or security_ans.text == "":
            print("Please Fill in All Fields")

        elif len(password.text) < 8:
            print("Password Too Short!")
            return

        else:
            values = (email.text.strip(), password.text.strip(), fname.text.strip(), lname.text.strip(), security_ans.text.strip())
            mycursor.execute(sql_sign_up, values)
            mydb.commit()
            toast("Successfully Signed Up")
            email.text = ""
            password.text = ""


class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.store = JsonStore("daily_popup.json")

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