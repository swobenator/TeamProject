from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import BooleanProperty
from kivymd.uix.button import MDIconButton

# Damien imports
from kivy.clock import \
    Clock  # Import allows scheduling task (Side note: This has built in properties like Clock.schedule_interval() which acts like a loop), Source: https://kivy.org/doc/stable/api-kivy.clock.html
from kivy.core.audio import SoundLoader  # Loads and plays sound files.
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.screenmanager import Screen
import os
import json

# Set the window size
Window.size = (400, 720)
SOUNDS_FOLDER = "sounds"  # Path to sound files
DATA_FILE = "habit_data.json"


# beginning of mediation code

# Usage of Inheritance, MeditationScreen is a subclass/child of Screen(parent)
class MeditationScreen(Screen):
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
        """Starts or resumes the meditation timer and sound playback."""
        if self.timer: return  # Timer already running

        self.time_left = self.time_left or 60  # Default to 10 minutes if not set
        self.update_timer_label()

        self.stop_sound()  # Stops currently playing sound

        # Set default sound if there is no selected sound
        self.selected_sound_path = self.selected_sound_path or os.path.join(SOUNDS_FOLDER, "Default.mp3")
        self.play_sound(repeat=True)  # Setting it as True allows to play sound in a loop
        self.timer = Clock.schedule_interval(self.update_time, 1)

    def update_time(self, dt):
        """Updates the timer each second."""
        if self.time_left > 0:
            self.time_left -= 1  # Decreasing time left by 1 second
            self.update_timer_label()  # Updates UI dynamically
        elif self.time_left == 0 and self.timer:  # Ensures this runs only when timer was running
            self.cancel_timer()  # stops the timer
            self.stop_sound()  # stops the meditation sound
            self.show_end_message()  # Pop-up and play end sound

    def update_timer_label(self):
        """Updates the timer label in MM:SS format."""
        self.timer_label_text = f"{self.time_left // 60:02}:{self.time_left % 60:02}"
        if 'timer_label' in self.ids:
            self.ids.timer_label.text = self.timer_label_text

    def show_end_message(self):
        """Displays a popup when meditation time is up."""
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

    def dismiss_message(self):
        """Stops the alarm sound"""
        if self.alarm_sound:  # Stops alarm if it's playing
            self.alarm_sound.stop()
            self.alarm_sound = None  # reset

        if self.end_dialog:
            self.end_dialog.dismiss()  # clos the pop-up

    def play_end_sound(self):
        """Plays alarm when the session ends"""
        end_sound_path = os.path.join(SOUNDS_FOLDER, "alarm.mp3")
        self.alarm_sound = SoundLoader.load(end_sound_path)  # Stores the instance in self.alarm_sound

        if self.alarm_sound:
            self.alarm_sound.play()  # Plays the end sound

    def pause_timer(self):
        """Pauses the timer and sound playback but keeps the remaining time intact."""
        self.cancel_timer()
        self.stop_sound()

    def reset_timer(self):
        """Resets the timer display to 00:00 and prevents the end message from showing."""
        self.cancel_timer()  # Ensure the timer is stopped
        self.stop_sound()
        self.time_left = 0
        self.timer_label_text = "00:00"  # Set text manually to prevent triggering update_time()

        if 'timer_label' in self.ids:
            self.ids.timer_label.text = self.timer_label_text

    def select_sound(self, sound_filename):
        """Plays a short snippet of the selected sound."""
        self.stop_sound()  # Stop any currently playing sound
        self.selected_sound_path = os.path.join(SOUNDS_FOLDER, sound_filename)
        self.play_sound(repeat=False)  # Setting it as False only plays once
        Clock.schedule_once(lambda dt: self.stop_sound(), 5)  # Play snippet for 5 sec because

        if self.timer:  # If the timer is running, restart the selected sound in a loop after the snippet
            Clock.schedule_once(lambda dt: self.play_sound(repeat=True), 5)  # Resume after 5 sec

    def play_sound(self, repeat=False):
        """Handles sound playback."""
        self.stop_sound()  # Stop any existing playing sound
        self.current_sound = SoundLoader.load(
            self.selected_sound_path)  # Load selected sound file into self.current_sound.
        if self.current_sound:  # Check if the sound was loaded.
            self.current_sound.repeat = repeat  # Enables looping if it's required
            self.current_sound.play()  # Play the sound

    def stop_sound(self):
        """Stops sound playback."""
        if self.current_sound:
            self.current_sound.stop()  # Stops playback when calling the built-in stop() method.
            self.current_sound = None  # Reset the current_sound to none so the system knows no sound is currently active

    def cancel_timer(self):
        """Cancels the running countdown timer if it is active."""
        if self.timer:
            self.timer.cancel()  # Using the .cancel built in property allows repeated calls being stopped.
            self.timer = None

    def on_leave(self):
        """Automatically stop the timer and sound when leaving the meditation screen."""
        self.cancel_timer()  # Stop the timer
        self.stop_sound()  # Stop any playing sound

        # end of mediation code

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
class HabitTrackerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_days = []  # will store selected days
        self.habits = self.load_habits()  # Store habits categorized by days
        self.dialog = None  # the habit input dialog

    def load_habits(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                self.habits = json.load(f)  # Load habits from file
                return self.habits
        else:
            self.habits = {}
            return self.habits

#Save habits to a JSON
    def save_habits(self):
        data = {}
        for day, habits in self.habits.items():
            data[day] = [{"habit": habit} for habit in habits]

        with open(DATA_FILE, "w") as f:
            json.dump(self.habits, f, indent=4)


    def toggle_day_selection(self, button):
        day = button.text

        if day in self.selected_days:
            self.selected_days.remove(day)
            app = MDApp.get_running_app()
            settings_screen = app.root.ids.screen_manager.get_screen("settings")
            button.md_bg_color = settings_screen.theme_cls.primary_color
        else:
            self.selected_days.append(day)
            button.md_bg_color = [0, 0, 0, 0]

        self.filter_habits()  # Update UI

#opens a dialog box to add a new habit
    def add_habit_dialog(self):
        if not self.dialog:
            self.dialog_content = HabitInputDialog()
            self.dialog = MDDialog(
                title=" ",
                type="custom",
                content_cls=self.dialog_content,
                buttons=[
                    MDFlatButton(text="CANCEL", on_release=lambda x: self.dialog.dismiss()),
                    MDFlatButton(text="ADD",
                                 on_release=lambda x: self.add_habit(self.dialog_content.habit_input.text)),
                ],
            )
        self.dialog.open()


#Adds the new habit and saves the info to the JSON
    def add_habit(self, habit_name):
        habit_name = habit_name.strip()
        if not habit_name or not self.selected_days:
            return

        for day in self.selected_days:
            if day not in self.habits:
                self.habits[day] = []

            if habit_name not in self.habits[day]:
                self.habits[day].append(habit_name)

        self.save_habits()  # Save after adding
        self.dialog.dismiss()
        self.filter_habits()  # Refresh UI


#Creates and displays the new habit on a MDCard
    def add_habit_card(self, habit_name, day):
        for card in self.ids.habits_list.children:
            if hasattr(card, "habit_name") and card.habit_name == habit_name:
                return  # Prevent duplicate habit cards

        card = MDCard(
            orientation="vertical",
            size_hint=(0.9, None),
            height="115dp",
            pos_hint={"center_x": 0.5},
            elevation=10,
            padding="10dp",
        )

        card.habit_name = habit_name  # Store habit name to prevent duplicates

        #Bin icon to removes the habit from the screen
        label = MDLabel(text=habit_name, halign="center")
        delete_button = MDIconButton(
            icon="trash-can",
            on_release=lambda x: self.delete_habit(habit_name, day, card)
        )

        card.add_widget(label)
        card.add_widget(delete_button)

        self.ids.habits_list.add_widget(card)
        self.ids.habits_list.height += card.height  # Adjust height


#function to delete the habit.
    def delete_habit(self, habit_name, day, card):
        if day in self.habits and habit_name in self.habits[day]:
            self.habits[day].remove(habit_name)
            if not self.habits[day]:  # Remove empty lists
                del self.habits[day]

            self.ids.habits_list.remove_widget(card)  # Remove habit card from UI
            self.save_habits()  # Save the updated habits list

#Function to show the only habit based on day slected
    def filter_habits(self):
        habits_list = self.ids.habits_list
        habits_list.clear_widgets()  # Remove all habit cards

        unique_habits = set()  # Track unique habits to avoid duplicates

        for day in self.selected_days:
            if day in self.habits:
                for habit in self.habits[day]:
                    if habit not in unique_habits:  # Prevent duplicate UI elements
                        unique_habits.add(habit)
                        self.add_habit_card(habit, day)  # Display habit

        habits_list.height = len(unique_habits) * 120  # Approximate height per habit card


# Settings Screen
class SettingsScreen(Screen):
    dark_mode = BooleanProperty(False)
    notifications_enabled = BooleanProperty(False)
    theme_colors = ["Blue", "Red", "Green", "Purple", "Indigo"]
    current_theme_index = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls = MDApp.get_running_app().theme_cls  # Get theme class from MDApp
        self.theme_cls.theme_style = "Light"  # Set the initial theme style

    def toggle_dark_mode(self, instance, value):
        self.dark_mode = value
        self.update_theme()

    def toggle_notifications(self, instance, value):
        self.notifications_enabled = value

    def change_theme(self):
        self.current_theme_index = (self.current_theme_index + 1) % len(self.theme_colors)
        self.theme_cls.primary_palette = self.theme_colors[self.current_theme_index]
        self.update_theme()

    def update_theme(self):
        if self.dark_mode:
            self.theme_cls.theme_style = "Dark"
            Window.clearcolor = (0.1, 0.1, 0.1, 1)
        else:
            self.theme_cls.theme_style = "Light"
            Window.clearcolor = (1, 1, 1, 1)



# Main App
class MyApp(MDApp):
    def build(self):
        screen_manager = ScreenManager()
        screen_manager.add_widget(MeditationScreen(name="meditation"))
        screen_manager.add_widget(HabitTrackerScreen(name="habit_tracker"))
        screen_manager.add_widget(SettingsScreen(name="settings"))

        return Builder.load_file("settings.kv")


if __name__ == "__main__":
    MyApp().run()
