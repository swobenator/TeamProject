from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.segmentedbutton import MDSegmentedButton, MDSegmentedButtonItem
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import BooleanProperty

# Set the window size
Window.size = (400, 720)


class HabitInputDialog(MDBoxLayout):
    """Custom content for the habit input popup"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.habit_name = ""
        self.orientation = "vertical"
        self.spacing = "10dp"
        self.status_buttons = MDBoxLayout(orientation="horizontal",spacing="12dp")
        self.add_widget(self.status_buttons)


class HabitTrackerScreen(MDScreen):
    dialog = None
    dialog_content = None
    selected_days = []  # List to store selected days

    def toggle_day_selection(self, button):
        """Toggles selection of a day and tracks selected days."""
        if button.text in self.selected_days:
            self.selected_days.remove(button.text)
            button.md_bg_color = self.theme_cls.primary_light
        else:
            self.selected_days.append(button.text)
            button.md_bg_color = self.theme_cls.primary_color

    def add_habit_dialog(self):
        """Opens a dialog to enter a new habit name and select status"""
        if not self.dialog:
            self.dialog_content = MDTextField(
                hint_text="Enter your new habit",
                multiline=False
            )

            self.dialog = MDDialog(
                title="Add New Habit",
                type="custom",
                content_cls=self.dialog_content,
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                    MDFlatButton(
                        text="ADD",
                        on_release=self.add_habit
                    ),
                ],
            )
        self.dialog.open()

        def add_habit(self):
            """Retrieve the habit's text, then close the dialog."""
            new_habit = self.dialog_content.text
            # Here you can store 'new_habit' to your data model, database, etc.
            print(f"New habit entered: {new_habit}")
            self.dialog.dismiss()

class SettingsScreen(MDScreen):
    pass


class MyApp(MDApp):
    dark_mode = BooleanProperty(False)
    notifications_enabled = BooleanProperty(False)
    theme_colors = ["Blue", "Red", "Green", "Purple", "Indigo"]
    current_theme_index = 0

    def build(self):
        self.theme_cls.theme_style = "Light"
        return Builder.load_file("settings.kv")

    def toggle_dark_mode(self, instance, value):
        self.dark_mode = value
        self.update_theme()

    def toggle_notifications(self, instance, value):
        self.notifications_enabled = value

    def change_theme(self):
        self.current_theme_index = (self.current_theme_index + 1) % len(self.theme_colors)
        self.theme_color = self.theme_colors[self.current_theme_index]
        self.theme_cls.primary_palette = self.theme_color
        self.update_theme()

    def update_theme(self):
        if self.dark_mode:
            self.theme_cls.theme_style = "Dark"
            Window.clearcolor = (0.1, 0.1, 0.1, 1)
        else:
            self.theme_cls.theme_style = "Light"
            Window.clearcolor = (1, 1, 1, 1)

    dialog = None
    dialog_content = None
    selected_days = []  # List to store selected days

    def toggle_day_selection(self, button):
        """Toggles selection of a day and tracks selected days."""
        if button.text in self.selected_days:
            self.selected_days.remove(button.text)
            button.md_bg_color = self.theme_cls.primary_light
        else:
            self.selected_days.append(button.text)
            button.md_bg_color = self.theme_cls.primary_color

    def add_habit_dialog(self):
        """Opens a dialog to enter a new habit name and select status"""
        if not self.dialog:
            self.dialog_content = MDTextField(
                hint_text="Enter your new habit",
                multiline=False
            )

            self.dialog = MDDialog(
                title="Add New Habit",
                type="custom",
                content_cls=self.dialog_content,
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                    MDFlatButton(
                        text="ADD",
                        on_release=self.add_habit
                    ),
                ],
            )
        self.dialog.open()

    def add_habit(self, instance):
        """Retrieve the habit's text, then close the dialog."""
        new_habit = self.dialog_content.text
        # Here you can store 'new_habit' to your data model, database, etc.
        print(f"New habit entered: {new_habit}")
        self.dialog.dismiss()

if __name__ == "__main__":
    MyApp().run()
