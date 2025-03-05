from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import BooleanProperty

# Set the window size
Window.size = (400, 720)

# Custom content for the habit input popup
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

class SettingsScreen(MDScreen):
    """Settings screen"""
    pass

class MyApp(MDApp):
    dark_mode = BooleanProperty(False)
    notifications_enabled = BooleanProperty(False)
    theme_colors = ["Blue", "Red", "Green", "Purple", "Indigo"]
    current_theme_index = 0

    def build(self):
        self.theme_cls.theme_style = "Light"
        return Builder.load_file("settings.kv")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_days = [] #will store selected days
        self.habits = {}  # Store habits categorized by days
        self.dialog = None  # the habit input dialog

    def toggle_dark_mode(self, instance, value):
        """Toggle between light and dark mode"""
        self.dark_mode = value
        self.update_theme()

    def toggle_notifications(self, instance, value):
        """Toggle notifications"""
        self.notifications_enabled = value

    def change_theme(self):
        """Change the app's primary theme color"""
        self.current_theme_index = (self.current_theme_index + 1) % len(self.theme_colors)
        self.theme_cls.primary_palette = self.theme_colors[self.current_theme_index]
        self.update_theme()

    def update_theme(self):
        """Apply the selected theme style"""
        if self.dark_mode:
            self.theme_cls.theme_style = "Dark"
            Window.clearcolor = (0.1, 0.1, 0.1, 1)
        else:
            self.theme_cls.theme_style = "Light"
            Window.clearcolor = (1, 1, 1, 1)

    def toggle_day_selection(self, button):
        """Toggles selection of a day and tracks selected days."""
        day = button.text
        if button.text in self.selected_days:
            self.selected_days.remove(day)
            button.md_bg_color = [0, 0, 0, 0]
        else:
            self.selected_days.append(day)
            button.md_bg_color = self.theme_cls.primary_color

    def add_habit_dialog(self):
        """Opens a dialog to input a new habit"""
        if not self.dialog:
            self.dialog_content = HabitInputDialog()
            self.dialog = MDDialog(
                title=" ",
                type="custom",
                content_cls=self.dialog_content,
                buttons=[
                    MDFlatButton(text="CANCEL", on_release=lambda x: self.dialog.dismiss()),
                    MDFlatButton(text="ADD", on_release=lambda x: self.add_habit(self.dialog_content.habit_input.text)),
                ],
            )
        self.dialog.open()

    def add_habit(self, habit_name):
        """Adds the habit to the selected days and displays it in an MDCard"""
        if habit_name.strip() and self.selected_days:
            for day in self.selected_days:
                if day not in self.habits:
                    self.habits[day] = []
                self.habits[day].append(habit_name)

            # Create the habit card
            card = MDCard(
                orientation="vertical",
                size_hint=(0.9, None),
                height="80dp",
                pos_hint={"center_x": 0.5},
                elevation=10,
                padding="10dp"
            )
            card.add_widget(MDLabel(text=habit_name, halign="center"))

            # Adds a  card to the screen
            if self.root and self.root.ids.get("habits_list"):
                self.root.ids.habits_list.add_widget(card)
            # This will Update height dynamically
            self.root.ids.habits_list.height += card.height


            # Clear input field and close dialog
            self.dialog_content.habit_input.text = ""
            self.dialog.dismiss()

if __name__ == "__main__":
    MyApp().run()
