#Author: Damien Ho

from kivymd.app import MDApp #Essential for the using of KivyMD components, Source: https://kivymd.readthedocs.io/en/latest/themes/material-app/
from kivy.lang import Builder #This loads the .kv file, Source: https://kivy.org/doc/stable/api-kivy.lang.html#kivy.lang.Builder
from kivy.uix.screenmanager import Screen #This import I used to handle switching between screens. Source: https://kivy.org/doc/stable-1.11.0/api-kivy.uix.screenmanager.html
from kivy.clock import Clock #Import allows scheduling task (Side note: This has built in properties like Clock.schedule_interval() which acts like a loop), Source: https://kivy.org/doc/stable/api-kivy.clock.html
from kivy.core.window import Window #Allowd me to set the window properties such as size.
from kivy.core.audio import SoundLoader #Loads and plays sound files.
from kivy.properties import NumericProperty, StringProperty#Import that allows dynamic UI updates, Source:https://kivy.org/doc/stable/api-kivy.properties.html#kivy.properties.NumericProperty , https://kivy.org/doc/stable/api-kivy.properties.html#kivy.properties.StringProperty
import os#Used for handling file paths, Source: https://www.w3schools.com/python/module_os.asp?ref=escape.tech
import json
#This is UI components imported for just pop-up dialog, Source: https://kivymd.readthedocs.io/en/1.1.1/components/dialog/index.html
from kivymd.uix.dialog import MDDialog #This shows the pop-up
from kivymd.uix.button import MDFlatButton #Used this for a button in the pop-up
from kivymd.uix.list import OneLineListItem
from kivymd.uix.card import (
    MDCardSwipe,  MDCardSwipeLayerBox, MDCardSwipeFrontBox
)
from kivymd.uix.boxlayout import MDBoxLayout
from datetime import datetime
from kivy.uix.scrollview import ScrollView
from kivymd.uix.textfield import MDTextField
import uuid #Genrates unique identifiers (UUIDS) to uniquely identify items


Window.size = (400, 720)  # Set the window size for mobile-friendly resolution.
SOUNDS_FOLDER = "sounds"  # Path to sound files
JOURNAL_FILE = "journal.json"


class MainScreen(Screen):
    pass

#Usage of Inheritance, MeditationScreen is a subclass/child of Screen(parent)
class MeditationScreen(Screen):
    time_left = NumericProperty(0) #Updates UI automatically
    timer_label_text = StringProperty("00:00") #The timer display in sync. This property type can store a string that updates text based UI elements like 'MDLabel'

    #Constructor for MeditationScreen
    def __init__(self, **kwargs): #**kwargs allows passing additional arguments if you don't know how many, Source: https://www.w3schools.com/python/gloss_python_function_arbitrary_keyword_arguments.asp
        super().__init__(**kwargs) #Calls the parent class constructor (Screen)
        self.timer = None #Stores the clock event for the timer
        self.current_sound = None #Initialized variable to store the currently playing sound
        self.selected_sound_path = None #Initialized variable to store the file path of selected meditation sound, e.g.,"sounds/Ocean.mp3".
        self.alarm_sound = None

    def start_timer(self):
        """Starts or resumes the meditation timer and sound playback."""
        if self.timer: return  # Timer already running

        self.time_left = self.time_left or 600  # Default to 10 minutes if not set
        self.update_timer_label()

        self.stop_sound() #Stops currently playing sound

        #Set default sound if there is no selected sound
        self.selected_sound_path = self.selected_sound_path or os.path.join(SOUNDS_FOLDER, "Default.mp3")
        self.play_sound(repeat=True)#Setting it as True allows to play sound in a loop
        self.timer = Clock.schedule_interval(self.update_time, 1)

    def update_time(self, dt):
        """Updates the timer each second."""
        if self.time_left > 0:
            self.time_left -= 1  #Decreasing time left by 1 second
            self.update_timer_label() #Updates UI dynamically
        elif self.time_left == 0 and self.timer:  #Ensures this runs only when timer was running
            self.cancel_timer()#stops the timer
            self.stop_sound()#stops the meditation sound
            self.show_end_message()#Pop-up and play end sound

    def update_timer_label(self):
        """Updates the timer label in MM:SS format."""
        self.timer_label_text = f"{self.time_left // 60:02}:{self.time_left % 60:02}"
        if 'timer_label' in self.ids:
            self.ids.timer_label.text = self.timer_label_text

    def show_end_message(self):
        """Displays a popup when meditation time is up."""
        self.play_end_sound()

        #Close button for the dialog
        close_button = MDFlatButton(
            text="OK",
            on_release=lambda x: self.dismiss_message(),  #Dismiss pop-up when OK is clicked
            md_bg_color=(0.2, 0.6, 0.8, 1),  #color for the button
            text_color=(1, 1, 1, 1)  #text color
        )

        #Create the dialog pop-up
        self.end_dialog = MDDialog(
            title="Time's Up!",
            text="Meditation complete. You may continue or reset the session.",
            buttons=[close_button],
            radius = [20,20,20,20],#round corners
            auto_dismiss = False,
        )

        # Show the popup dialog
        self.end_dialog.open()

    def dismiss_message(self):
        """Stops the alarm sound"""
        if self.alarm_sound: #Stops alarm if it's playing
            self.alarm_sound.stop()
            self.alarm_sound = None # reset

        if self.end_dialog:
            self.end_dialog.dismiss()#clos the pop-up

    def play_end_sound(self):
        """Plays alarm when the session ends"""
        end_sound_path = os.path.join(SOUNDS_FOLDER, "alarm.mp3")
        self.alarm_sound = SoundLoader.load(end_sound_path)#Stores the instance in self.alarm_sound

        if self.alarm_sound:
            self.alarm_sound.play()#Plays the end sound

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
        self.stop_sound() #Stop any currently playing sound
        self.selected_sound_path = os.path.join(SOUNDS_FOLDER, sound_filename)
        self.play_sound(repeat=False) #Setting it as False only plays once
        Clock.schedule_once(lambda dt: self.stop_sound(), 5)  # Play snippet for 5 sec because

        if self.timer:# If the timer is running, restart the selected sound in a loop after the snippet
            Clock.schedule_once(lambda dt: self.play_sound(repeat=True), 5)  # Resume after 5 sec

    def play_sound(self, repeat=False):
        """Handles sound playback."""
        self.stop_sound()  # Stop any existing playing sound
        self.current_sound = SoundLoader.load(self.selected_sound_path)#Load selected sound file into self.current_sound.
        if self.current_sound:#Check if the sound was loaded.
            self.current_sound.repeat = repeat #Enables looping if it's required
            self.current_sound.play()#Play the sound

    def stop_sound(self):
        """Stops sound playback."""
        if self.current_sound:
            self.current_sound.stop()#Stops playback when calling the built-in stop() method.
            self.current_sound = None#Reset the current_sound to none so the system knows no sound is currently active

    def cancel_timer(self):
        """Cancels the running countdown timer if it is active."""
        if self.timer:
            self.timer.cancel()#Using the .cancel built in property allows repeated calls being stopped.
            self.timer = None

    def on_leave(self):
        """Automatically stop the timer and sound when leaving the meditation screen."""
        self.cancel_timer()  # Stop the timer
        self.stop_sound()  # Stop any playing sound

class JournalScreen(Screen):
    def __init__(self, **kwargs):
        """Initializes the journal screen and loads saved entries from file"""
        super().__init__(**kwargs)
        self.entries = []#Holds all journal entries (active and archived)
        self.archive_view = False#viewing archived entries
        self.load_entries()#Load existing entries on start

    def on_kv_post(self, base_widget):
        #update the list view after the UI is loaded.
        self.update_rv_data()

    def load_entries(self):
        #load journal entries from a JSON file if it exist
        if os.path.exists(JOURNAL_FILE):
            with open(JOURNAL_FILE, "r") as f:
                self.entries = json.load(f)
        else:
            self.entries = []#fallback: start with empty list

    def save_entries(self):
        #Save current list of entries to a JSON file
        with open(JOURNAL_FILE, "w") as f:
            json.dump(self.entries, f)

    def update_rv_data(self):
        #update the list view data based on whether archived entries are shown
        if self.archive_view:
            #filtering archived entries only
            data = [e for e in self.entries if e.get("archived", False)]
            self.ids.archive_label.opacity = 1 if not data else 0#show message if no archived entries
        else:
            #flitering active entries only
            data = [e for e in self.entries if not e.get("archived", False)]
            self.ids.archive_label.opacity = 0#hide label in active mode

        self.ids.rv.data = data#update the RecycleView's data


    def add_entry(self):
        """Adds a new journal entry from the text input. Uses .strip() to prevent blank entries with only whitespace."""
        entry_text = self.ids.entry_text.text
        if entry_text.strip(): #using .strip() to check for non-empty text
            new_entry = {
                "entry_id": str(uuid.uuid4()),#generate a unique ID for the entry
                "text": entry_text,
                "date": datetime.now().strftime("%b %d, %Y • %I:%M %p"),
                "archived": False,#default is active, not archived
            }
            self.entries.append(new_entry)#append new enetry to the list
            self.save_entries()#write changes to file
            self.update_rv_data()#refresh the RecycleView
            self.ids.entry_text.text = ""#clear text input

    def remove_entry(self, entry_id):
        """Deletes a journal entry using its unique ID. Uses a list comprehension to filter out the matching entry."""
        self.entries = [e for e in self.entries if e["entry_id"] != entry_id]#remove the entry
        self.save_entries()
        self.update_rv_data()

    def archive_entry(self, entry_id):
        """Marks an entry as archived so it no longer shows in active view.Looping through entries to find a match by ID."""
        for e in self.entries:#looping through all entries
            if e["entry_id"] == entry_id:
                e["archived"] = True#set as archived
                break
        self.save_entries()
        self.update_rv_data()

    def toggle_archive_view(self):
        """Switches between viewing active and archived entries.Also updates the button label accordingly."""
        self.archive_view = not self.archive_view #Flip the view mode
        self.ids.toggle_archive_btn.text = (
            "Back to Journal" if self.archive_view else "View Archive"
        )
        self.update_rv_data()

    def open_entry_dialog(self, entry_id):
        """Opens a popup dialog to view/edit an entry’s text.Finds the entry using its unique ID."""
        entry_to_edit = next((e for e in self.entries if e["entry_id"] == entry_id), None)#find the entry with matching ID
        if not entry_to_edit:
            return#entry not found, do nothing

        #layout for the popup content
        container = MDBoxLayout(orientation="vertical", size_hint_y=None, height="300dp")
        scroll = ScrollView()
        text_field = MDTextField(
            text=entry_to_edit["text"],
            multiline=True,
            size_hint_y=None,
            height="300dp"
        )
        scroll.add_widget(text_field)
        container.add_widget(scroll)

        #define save button action
        def on_save(instance):
            entry_to_edit["text"] = text_field.text#update entry text
            self.save_entries() #save to file
            self.update_rv_data() #refresh entry list
            dialog.dismiss() #close the popup

        #define cancel button action
        def on_cancel(instance):
            dialog.dismiss()

        dialog = MDDialog(
            title="View / Edit Entry",
            type="custom",
            content_cls=container,
            buttons=[
                MDFlatButton(text="Cancel", on_release=on_cancel),
                MDFlatButton(text="Save", on_release=on_save)
            ]
        )
        dialog.open()


# class JournalScreen(Screen):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.entries = []
#         self.archived_entries = []
#         self.show_archived = False
#         self.dialog = None
#         self.load_entries()
#
#     def on_pre_enter(self):
#         self.update_journal_list()
#
#     def load_entries(self):
#         """Loads journal entries from the JSON file."""
#         try:
#             with open(JOURNAL_FILE, 'r') as file:
#                 data = json.load(file)
#                 self.entries = data.get("entries", [])
#                 self.archived_entries = data.get("archived_entries", [])
#         except (FileNotFoundError, json.JSONDecodeError):
#             # If the file doesn't exist or is corrupted, start with empty lists
#             self.entries = []
#             self.archived_entries = []
#
#     def save_entry(self):
#         """Saves a new entry journal"""
#         entry_text = self.ids.journal_input.text
#         if entry_text:
#             creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             entry = {'text': entry_text, 'date': creation_date, 'archived': False}
#             self.entries.append(entry)
#             self.ids.journal_input.text = ''
#             self.update_journal_list()
#             self.save_entries_to_file()  # Save changes
#
#     def update_journal_list(self):
#         self.ids.journal_list.clear_widgets()
#         entries_to_display = self.archived_entries if self.show_archived else self.entries
#
#         if self.show_archived and not entries_to_display:
#             no_archive_item = OneLineListItem(text="No archived entries.")
#             self.ids.journal_list.add_widget(no_archive_item)
#         else:
#             for entry in entries_to_display:
#                 list_item = OneLineListItem(
#                     text=f"{entry['date']}: {entry['text'][:30]}...",
#                 )
#                 list_item.bind(on_release=partial(self.edit_entry, entry))
#                 self.ids.journal_list.add_widget(list_item)
#
#                 # list_item = OneLineListItem(
#                 #     text=f"{entry['date']}: {entry['text'][:30]}...",
#                 # )
#                 # list_item.bind(on_release=partial(self.edit_entry, entry))
#                 # self.ids.journal_list.add_widget(list_item)
#
#     def edit_entry(self, entry, instance):
#         content = BoxLayout(orientation='vertical', spacing="10dp")
#         text_input = TextInput(text=entry['text'], multiline=True)
#         content.add_widget(text_input)
#
#         content.add_widget(MDRaisedButton(
#             text="Save Edited Entry",
#             on_release=partial(self.save_edited_entry, entry, text_input)
#         ))
#
#         content.add_widget(MDRaisedButton(
#             text="Archive Entry", on_release=partial(self.confirm_archive_entry, entry)
#         ))
#
#         self.popup = Popup(title="Edit Entry", content=content, size_hint=(0.8, 0.8))
#         self.popup.open()
#
#     def save_edited_entry(self, entry, text_input, btn=None):
#         entry['text'] = text_input.text
#         self.popup.dismiss()
#         self.update_journal_list()
#         self.save_entries_to_file()  # Save changes
#
#     def confirm_archive_entry(self, entry, btn=None):
#         if not self.dialog:
#             self.dialog = MDDialog(
#                 title="Confirm Archive",
#                 text="Are you sure you want to archive this entry?",
#                 buttons=[
#                     MDFlatButton(text="CANCEL", on_release=self.dismiss_dialog),
#                     MDFlatButton(text="CONFIRM", on_release=partial(self.archive_entry, entry))
#                 ],
#             )
#         self.dialog.open()
#
#     def dismiss_dialog(self, instance):
#         self.dialog.dismiss()
#
#     def archive_entry(self, entry, btn=None):
#         if entry in self.entries:
#             self.entries.remove(entry)
#             self.archived_entries.append(entry)
#         else:
#             self.archived_entries.remove(entry)
#             self.entries.append(entry)
#
#         self.dismiss_dialog(None)
#         self.popup.dismiss()
#         self.update_journal_list()
#         self.save_entries_to_file()  # Save changes
#
#     def toggle_archive(self):
#         self.show_archived = not self.show_archived
#         # Update the toggle button text via its id.
#         self.ids.archive_toggle_button.text = "Back to Journal" if self.show_archived else "View Archived Entries"
#         self.update_journal_list()
#
#     def save_entries_to_file(self):
#         """Saves the current journal entries to the JSON file."""
#         data = {
#             "entries": self.entries,
#             "archived_entries": self.archived_entries,
#         }
#         with open(JOURNAL_FILE, 'w') as file:
#             json.dump(data, file, indent=4)


class ChatbotScreen(Screen):
    pass


class HamburgerApp(MDApp):#Inherits MDApp
    def build(self):
        return Builder.load_file("menu.kv")#loads and applies the UI from 'menu.kv'

#Runs the app
if __name__ == '__main__':
    HamburgerApp().run()
