#Author: Damien Ho

from kivymd.app import MDApp #Essential for the using of KivyMD components, Source: https://kivymd.readthedocs.io/en/latest/themes/material-app/
from kivy.lang import Builder #This loads the .kv file, Source: https://kivy.org/doc/stable/api-kivy.lang.html#kivy.lang.Builder
from kivy.uix.screenmanager import Screen #This import I used to handle switching between screens. Source: https://kivy.org/doc/stable-1.11.0/api-kivy.uix.screenmanager.html
from kivy.clock import Clock #Import allows scheduling task (Side note: This has built in properties like Clock.schedule_interval() which acts like a loop), Source: https://kivy.org/doc/stable/api-kivy.clock.html
from kivy.core.window import Window #Allowd me to set the window properties such as size. Source: https://kivy.org/doc/stable/api-kivy.core.window.html
from kivy.core.audio import SoundLoader #Loads and plays sound files. Source: https://kivy.org/doc/stable/api-kivy.core.audio.html
from kivy.properties import NumericProperty, StringProperty#Import that allows dynamic UI updates, Source:https://kivy.org/doc/stable/api-kivy.properties.html#kivy.properties.NumericProperty , https://kivy.org/doc/stable/api-kivy.properties.html#kivy.properties.StringProperty
import os#Used for handling file paths, Source: https://www.w3schools.com/python/module_os.asp?ref=escape.tech
import json
#This is UI components imported for just pop-up dialog, Source: https://kivymd.readthedocs.io/en/1.1.1/components/dialog/index.html
from kivymd.uix.dialog import MDDialog #This shows the pop-up
from kivymd.uix.button import MDFlatButton #Used this for a button in the pop-up
# from kivymd.uix.list import OneLineListItem
# from kivymd.uix.card import (
#     MDCardSwipe,  MDCardSwipeLayerBox, MDCardSwipeFrontBox
# )
from kivymd.uix.boxlayout import MDBoxLayout #Use this for arraging widgets
from datetime import datetime #This imports allows us to get the current date and time
from kivy.uix.scrollview import ScrollView #This allows scrolling inside the dialogs
from kivymd.uix.textfield import MDTextField
import uuid #Genrates unique identifiers (UUIDS) to uniquely identify items


Window.size = (400, 720)  #seets the window size for mobile-friendly resolution.
SOUNDS_FOLDER = "sounds"  #This is the path to sound files
JOURNAL_FILE = "journal.json" #A file where the journal entries are going to be stored



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
        #starts or resumes the meditation timer and sound playback.
        if self.timer: return  #check if timer already running and if yes, exit and do nothing

        self.time_left = self.time_left or 600  # Default to 10 minutes if not set
        self.update_timer_label() #Show the time on screen

        self.stop_sound() #Stops currently playing sound

        #Set default sound if there is no selected sound
        self.selected_sound_path = self.selected_sound_path or os.path.join(SOUNDS_FOLDER, "Default.mp3")
        self.play_sound(repeat=True)#Setting it as True allows to play sound in a loop
        self.timer = Clock.schedule_interval(self.update_time, 1)

    def update_time(self, dt):
        #Updates the timer each second.
        if self.time_left > 0: #If time is still left
            self.time_left -= 1  #Decrease time left by 1 second
            self.update_timer_label() #Updates UI dynamically
        elif self.time_left == 0 and self.timer:  #Ensures this runs only when timer was running
            self.cancel_timer()#stops the timer
            self.stop_sound()#stops the meditation sound
            self.show_end_message()#Pop-up and play end sound

    def update_timer_label(self):
        #Updates the timer label in MM:SS format.
        self.timer_label_text = f"{self.time_left // 60:02}:{self.time_left % 60:02}"#f-string to format the updated time correctly
        if 'timer_label' in self.ids:#Check if the timer label exists in the .kv file
            self.ids.timer_label.text = self.timer_label_text #Updates UI label with formatted time

    def show_end_message(self):
        #Displays a popup when meditation time is up.
        self.play_end_sound()

        #Close button for the dialog, close_button is a local variable which will only be used in this function
        close_button = MDFlatButton(
            text="OK",
            on_release=lambda x: self.dismiss_message(),  #Dismiss pop-up when OK is clicked, Source: https://www.w3schools.com/python/python_lambda.asp
            md_bg_color=(0.2, 0.6, 0.8, 1),  #color for the button
            text_color=(1, 1, 1, 1)  #text color
        )

        #Create the dialog pop-up, self.end_dialog is a instance variable, so this will be reused in another function called dismiss_message()
        self.end_dialog = MDDialog(
            title="Time's Up!",
            text="Meditation complete. You may continue or reset the session.",
            buttons=[close_button],#add close button
            radius = [20,20,20,20],#round corners
            auto_dismiss = False,#prevent auto-closing when clicking outside
        )

        # Show the popup dialog
        self.end_dialog.open()

    def dismiss_message(self):
        #Stops the alarm sound
        if self.alarm_sound: #Stops alarm if it's playing
            self.alarm_sound.stop()#stop the sound
            self.alarm_sound = None # reset

        if self.end_dialog:#if the pop up exist
            self.end_dialog.dismiss()#clos the pop-up

    def play_end_sound(self):
        #Plays alarm when the session ends
        end_sound_path = os.path.join(SOUNDS_FOLDER, "alarm.mp3")
        self.alarm_sound = SoundLoader.load(end_sound_path)#Stores the instance in self.alarm_sound

        if self.alarm_sound:#checks if the loadin worked
            self.alarm_sound.play()#Plays the end sound/alarm sound

    def pause_timer(self):
        #Pauses the timer and sound playback but keeps the remaining time intact.
        self.cancel_timer()
        self.stop_sound()


    def reset_timer(self):
        #resets the timer display to 00:00 and prevents the end message from showing.
        self.cancel_timer()  # Ensure the timer is stopped
        self.stop_sound()#Stop
        self.time_left = 0
        self.timer_label_text = "00:00"  # Set text manually to prevent triggering update_time()

        if 'timer_label' in self.ids:
            self.ids.timer_label.text = self.timer_label_text

    def select_sound(self, sound_filename):
        #plays a short snippet of the selected sound.
        self.stop_sound() #Stop any currently playing sound
        self.selected_sound_path = os.path.join(SOUNDS_FOLDER, sound_filename)
        self.play_sound(repeat=False) #Setting it as False only plays once
        Clock.schedule_once(lambda dt: self.stop_sound(), 5)  # Play snippet for 5 sec because

        if self.timer:# If the timer is running, restart the selected sound in a loop after the snippet
            Clock.schedule_once(lambda dt: self.play_sound(repeat=True), 5)  # Resume after 5 sec

    def play_sound(self, repeat=False):
        #Handles sound playback.
        self.stop_sound()  # Stop any existing playing sound
        self.current_sound = SoundLoader.load(self.selected_sound_path)#Load selected sound file into self.current_sound.
        if self.current_sound:#Check if the sound was loaded.
            self.current_sound.repeat = repeat #Enables looping if it's required
            self.current_sound.play()#Play the sound

    def stop_sound(self):
        #Stops sound playback.
        if self.current_sound:#if timer exist
            self.current_sound.stop()#Stops playback when calling the built-in stop() method.
            self.current_sound = None#Reset the current_sound to none so the system knows no sound is currently active

    def cancel_timer(self):
        #Cancels the running countdown timer if it is active.
        if self.timer:#If the timer is currently active
            self.timer.cancel()#Using the .cancel built in property allows repeated calls being stopped.
            self.timer = None

    def on_leave(self):
        #Automatically stop the timer and sound when leaving the meditation screen.
        self.cancel_timer()  # Stop the timer
        self.stop_sound()  # Stop any playing sound

class JournalScreen(Screen):
    def __init__(self, **kwargs):
        #Initializes the journal screen and loads saved entries from file
        super().__init__(**kwargs)#Like the meditation timer, this calls the parent class constructor
        self.entries = []#Holds all journal entries (active and archived)
        self.archive_view = False#viewing archived entries
        self.load_entries()#Load existing entries on start

    def on_kv_post(self, base_widget):
        #update the list view after the UI is loaded.
        self.update_rv_data()

    def load_entries(self):
        #load journal entries from a JSON file if it exist
        if os.path.exists(JOURNAL_FILE):#If the file called journal.json exist in the directory
            with open(JOURNAL_FILE, "r") as f:#yes? then open the file so I can read("r") the saved entries
                self.entries = json.load(f)#f is for file(it's what I named it), load entries from file
        else:
            self.entries = []#fallback: start with empty list

    def save_entries(self):
        #Save current list of entries to a JSON file
        with open(JOURNAL_FILE, "w") as f:#create the file in write mode("w")
            json.dump(self.entries, f)#after it converts the entries list into JSON and write it to the file

    def update_rv_data(self):
        #update the list view data based on whether archived entries are shown
        if self.archive_view:
            #filtering archived entries only, I used data as a temporary variabl name to hold that filtered list
            data = [e for e in self.entries if e.get("archived", False)]#This loops through each entry (I named it "e") in the list self.entries and check if e has been archived(archived:true), if it doesn't, treat it as false.
            self.ids.archive_label.opacity = 1 if not data else 0#show message if no archived entries, opacity is a property in Kivy that controls the visibility, 1 = visible and 0 = invisible(but it still exist)
        else:
            #flitering active entries only
            data = [e for e in self.entries if not e.get("archived", False)]
            self.ids.archive_label.opacity = 0#hide label in active mode

        self.ids.rv.data = data#update the RecycleView's data


    def add_entry(self):
        #Adds a new journal entry from the text input. Uses .strip() to prevent blank entries with only whitespace.
        entry_text = self.ids.entry_text.text# entry_text is a local variable only for this function, I use the self.ids to give me access to all the widgets in my .kv that has the id:.
        if entry_text.strip(): #using .strip() to check for non-empty text, I need this because if someone s could just hit a spacebar and saves a blank entry
            new_entry = {#local variable only for this function
                "entry_id": str(uuid.uuid4()),#generate a unique/random ID for the entry, this helps me avoid duplicates and keeps the entries organized
                "text": entry_text,
                "date": datetime.now().strftime("%b %d, %Y • %I:%M %p"),#Get current time and format it to a readable strig then save it with the journal entry
                "archived": False,#default is active, not archived
            }
            self.entries.append(new_entry)#append new enetry to the list
            self.save_entries()#write changes to file, this function writes self.entries to the json file so that even if i close the app, the entry is saved
            self.update_rv_data()#refresh the RecycleView, this basically updates the screen so the entries appear immediately
            self.ids.entry_text.text = ""#clear text input so the user can type a new entry

    def remove_entry(self, entry_id):
        #Deletes a journal entry using its unique ID. Uses a list comprehension to filter out the matching entry.
        self.entries = [e for e in self.entries if e["entry_id"] != entry_id]#remove the entry, loop through each entry, keep it only if it's ID is not the one we are deleting, then overwrite the list with new filtered version
        self.update_rv_data()#refresh the ui on the screen and show latest version of the entries

    def archive_entry(self, entry_id):
        #Marks an entry as archived so it no longer shows in active view.Looping through entries to find a match by ID.
        for e in self.entries:#looping through all entries, e is a temporary variaqble I'm using to represent one entry at a time
            if e["entry_id"] == entry_id:#If it finds one with a matching ID
                e["archived"] = True#set as archived
                break
        self.save_entries()
        self.update_rv_data()

    def toggle_archive_view(self):
        #Switches between viewing active and archived entries.Also updates the button label accordingly.
        self.archive_view = not self.archive_view #Flip the view mode, toggle between true and false
        self.ids.toggle_archive_btn.text = (#seld.ids let me access widgets from the .kv, i'm changing the button label to match the current view
            "Back to Journal" if self.archive_view else "View Archive"
        )
        self.update_rv_data()

    def open_entry_dialog(self, entry_id):
        #Opens a popup dialog to view/edit an entry’s text.Finds the entry using its unique ID.
        entry_to_edit = next((e for e in self.entries if e["entry_id"] == entry_id), None)#find the entry with matching ID, return none if not found
        if not entry_to_edit:
            return#entry not found, do nothing

        #layout for the popup content
        container = MDBoxLayout(orientation="vertical", size_hint_y=None, height="300dp")#MDBoxLayout arranges child widgets in a row or column, i set the orientation in vertical and turn off automatic vertical sizing and i set a fixed height
        scroll = ScrollView()#this creates a scrollable area for the text field
        text_field = MDTextField(
            text=entry_to_edit["text"],
            multiline=True,
            size_hint_y=None,
            height="300dp"
        )#This is a text input box, it loads existing entry text so the user can view or edit it, it sets to be a multiline meaning the user can type paragraphs and also I have a fixed height for the pop up
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


class ChatbotScreen(Screen):
    pass


class HamburgerApp(MDApp):#Inherits MDApp
    def build(self):
        return Builder.load_file("menu.kv")#loads and applies the UI from 'menu.kv', this becomes the app.root which will be used in the .kv file

#Runs the app
if __name__ == '__main__':
    HamburgerApp().run()#Start the app
