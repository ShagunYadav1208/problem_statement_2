import tkinter
import tkinter.messagebox
import customtkinter
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import requests
from bs4 import BeautifulSoup
from tkinter import *
import customtkinter as ctk
import speech_recognition as sr
import pyttsx3
import wikipedia
import webbrowser
import pywhatkit
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import Toplevel
from tkinter import filedialog
from nltk.corpus import cmudict
from gtts import gTTS
import os
from spellchecker import SpellChecker
import language_tool_python

language = 'en-IN'

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.text_input = False

        # speak engine initialize
        self.engine = pyttsx3.init('sapi5')
        self.voices = self.engine.getProperty('voices')
        self.muted = False
        self.engine.setProperty('voice', self.voices[0].id)

        # Making Feedback file
        try:
            with open("Feedback.txt", "r") as file:
                flag = 1
        except Exception as e:
            with open("Feedback.txt", "w") as file:
                file.write("")
        
        # Making contacts file
        try:
            with open("contacts.txt", "r") as file:
                flag = 1
        except Exception as e:
            with open("contacts.txt", "w") as file:
                file.write("")

        self.contacts = {}

        with open("contacts.txt", "r") as file:
            for line in file:
                name, phone_number = line.strip().split(':')
                self.contacts[name] = phone_number
        
        # configure window
        self.title("Personal Assistant")
        self.geometry(f"{1100}x{580}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # Making Sidebar frame
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=5, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(20, weight=1) # Buttons in sidebar
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Settings", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode", anchor="w")
        self.appearance_mode_label.grid(row=1, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=2, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling", anchor="w")
        self.scaling_label.grid(row=3, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"], command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=4, column=0, padx=20, pady=(10, 20))
        self.AccentOptions = customtkinter.CTkLabel(self.sidebar_frame, text="Language:")
        self.AccentOptions.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.language_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["English", "Hindi", "Japanese", "French", "German", "Spanish"], command = self.change_language)
        self.language_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))

        # Making Feedback entry
        self.entry = customtkinter.CTkEntry(self, placeholder_text="Feedback")
        self.entry.grid(row=3, column=1, columnspan=2, padx=(20, 0), pady=(20, 20), sticky="nsew")
        self.main_button_1 = customtkinter.CTkButton(master=self, fg_color="transparent", border_width=2, text = "Submit", text_color=("gray10", "#DCE4EE"), command = self.Saving_to_file)
        self.main_button_1.grid(row=3, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew")

        # Making Text box
        self.textbox = customtkinter.CTkTextbox(self, width=250)
        self.textbox.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")

        # Making Contacts Section
        self.tabview = customtkinter.CTkTabview(self, width=250)
        self.tabview.grid(row=0, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.tabview.add("Add Contact")
        self.tabview.add("Contact List")
        self.tabview.add("Delete Contact")
        self.tabview.tab("Add Contact").grid_columnconfigure(0, weight=1)  # configure grid of individual tabs
        self.tabview.tab("Contact List").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Delete Contact").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Delete Contact").grid_rowconfigure(2, weight=1)

        self.name_entry = customtkinter.CTkEntry(self.tabview.tab("Add Contact"), placeholder_text = "Name")
        self.name_entry.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.number_entry = customtkinter.CTkEntry(self.tabview.tab("Add Contact"), placeholder_text = "Number")
        self.number_entry.grid(row=1, column=0, padx=20, pady=(10, 10))
        self.add_contact_button = customtkinter.CTkButton(self.tabview.tab("Add Contact"), text="Add Contact", command=self.adding)
        self.add_contact_button.grid(row=2, column=0, padx=20, pady=(10, 10))
        self.show_contact_button = customtkinter.CTkButton(self.tabview.tab("Contact List"), text="Show Contacts", command=self.show_contacts)
        self.show_contact_button.grid(row=0, column=0, padx=20, pady=20)
        self.delete_entry = customtkinter.CTkEntry(self.tabview.tab("Delete Contact"), placeholder_text = "Name")
        self.delete_entry.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.delete_contact_button = customtkinter.CTkButton(self.tabview.tab("Delete Contact"), text="Contact List", command=self.deleting)
        self.delete_contact_button.grid(row=1, column=0, padx=20, pady=20)

        # Making Text Input box
        self.AccentSelector_frame = customtkinter.CTkScrollableFrame(self, label_text="Text Input Box")
        self.AccentSelector_frame.grid(row=0, column=3, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.radio_var = tkinter.IntVar(value=0)
        self.text_box_switch = customtkinter.CTkSwitch(self.AccentSelector_frame, text = "Text Input", command = self.toggling)
        self.text_box_switch.grid(row=0, padx=(20, 10), pady=(10, 10))
        self.main_button_2 = customtkinter.CTkButton(self.AccentSelector_frame, fg_color="transparent", border_width=2, text = "💬", text_color=("gray10", "#DCE4EE"), command = self.calling)
        self.main_button_2.grid(row=2, padx=(40, 40), pady=(10, 10), sticky="nw")

        # Making listening button and volume bar and more
        self.slider_progressbar_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.slider_progressbar_frame.grid(row=1, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.slider_progressbar_frame.grid_columnconfigure(3, weight=1)
        self.slider_progressbar_frame.grid_rowconfigure(8, weight=1)
        self.listening_button = customtkinter.CTkButton(self.slider_progressbar_frame, width = 200, height = 100, corner_radius=100, text = "🎙️", command = self.calling)
        self.listening_button.grid(row=0, column=0, columnspan = 5, padx=(20, 10), pady=(10, 10), sticky="nsew")
        self.progressbar_1 = customtkinter.CTkProgressBar(self.slider_progressbar_frame)
        self.progressbar_1.grid(row=1, column=0, columnspan = 5, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.slider_1 = customtkinter.CTkSlider(self.slider_progressbar_frame, from_=0, to=1, number_of_steps=100)
        self.slider_1.grid(row=2, column=0, columnspan = 5, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.slider_1.bind("<Motion>", self.set_volume)
        self.progressbar_2 = customtkinter.CTkProgressBar(self.slider_progressbar_frame)
        self.progressbar_2.grid(row=3, column=0, columnspan = 5, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.volume_label = customtkinter.CTkLabel(self.slider_progressbar_frame, text = "Volume: ")
        self.volume_label.grid(row=4, column=0, columnspan = 5, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.save_button_speach = customtkinter.CTkButton(self.slider_progressbar_frame, text = "Get correct Pronounciation through Speach", command = self.saving_speach)
        self.save_button_speach.grid(row=5, column=0, columnspan = 1, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.save_button_text = customtkinter.CTkButton(self.slider_progressbar_frame, text = "Get correct Pronounciation through text", command = self.saving_text)
        self.save_button_text.grid(row=5, column=4, columnspan = 1, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.mute_switch = customtkinter.CTkSwitch(self.slider_progressbar_frame, text = "Mute", command = self.mute)
        self.mute_switch.grid(row=5, column=3, padx=(20, 10), pady=(10, 10))
        self.correct_button_Speach = customtkinter.CTkButton(self.slider_progressbar_frame, text = "Remove Gramatical and Spelling error through Speach", command = self.correct_speach)
        self.correct_button_Speach.grid(row=6, column=0, columnspan = 1, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.correct_button_text = customtkinter.CTkButton(self.slider_progressbar_frame, text = "Remove Gramatical and Spelling error through text", command = self.correct_text)
        self.correct_button_text.grid(row=6, column=4, columnspan = 1, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.clear_button = customtkinter.CTkButton(self.slider_progressbar_frame, text = "Clear Text Box", command = self.clear_text)
        self.clear_button.grid(row=6, column=3, padx=(20, 10), pady=(10, 10))

        # help text box
        self.help_box = customtkinter.CTkTextbox(self)
        self.help_box.grid(row=1, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")

        # Maker
        self.checkbox_slider_frame = customtkinter.CTkFrame(self)
        self.checkbox_slider_frame.grid(row=1, column=3, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.checkbox_slider_frame.grid_columnconfigure(0, weight=1)
        self.slider_progressbar_frame.grid_rowconfigure(6, weight=1)
        self.Made_label = customtkinter.CTkLabel(self.checkbox_slider_frame, text="Made by: ", font=customtkinter.CTkFont(size=20, weight="bold"), text_color=("purple", "#4e09a3"))
        self.Made_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.Name_Of_Maker_label = customtkinter.CTkLabel(self.checkbox_slider_frame, text="Shagun Yadav", font=customtkinter.CTkFont(size=17, weight="bold"), text_color=("cyan", "#09f0f0"))
        self.Name_Of_Maker_label.grid(row=1, column=0, padx=20, pady=(10, 0))
        self.Name_Of_Maker_label = customtkinter.CTkLabel(self.checkbox_slider_frame, text="Alok Yadav", font=customtkinter.CTkFont(size=17, weight="bold"), text_color=("cyan", "#09f0f0"))
        self.Name_Of_Maker_label.grid(row=2, column=0, padx=20, pady=(10, 0))
        self.Name_Of_Maker_label = customtkinter.CTkLabel(self.checkbox_slider_frame, text="Hamza", font=customtkinter.CTkFont(size=17, weight="bold"), text_color=("cyan", "#09f0f0"))
        self.Name_Of_Maker_label.grid(row=3, column=0, padx=20, pady=(10, 0))
        self.Guide_label = customtkinter.CTkLabel(self.checkbox_slider_frame, text="Guide: ", font=customtkinter.CTkFont(size=20, weight="bold"), text_color=("purple", "#4e09a3"))
        self.Guide_label.grid(row=4, column=0, padx=20, pady=(80, 10))
        self.Name_Of_Guide_label = customtkinter.CTkLabel(self.checkbox_slider_frame, text="Ms. Anuranjana", font=customtkinter.CTkFont(size=17, weight="bold"), text_color=("cyan", "#09f0f0"))
        self.Name_Of_Guide_label.grid(row=5, column=0, padx=20, pady=(10, 0))

        # default Values
        self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("100%")
        self.slider_1.configure(command=self.progressbar_2.set)
        self.progressbar_1.configure(mode="indeterminnate")
        self.progressbar_1.start()
        self.textbox.insert("0.0", "Hii, I am your assistant what can I do For You")
        self.help_box.insert("0.0", '''~~~~~~~~~~~~Help Box~~~~~~~~~~~~\n\n1. Send Message - Send message on Whatsapp\n\n2. Play something on youtube\n\n3. Search on google\n\n4. Just type - speech to text in text box\n\n5. Wikipedia someone - will get some lines from wikipedia\n\n6. Ponounce - will pronounce what ever you say\n\n7. Correct Grammer and Spelling\n\n8. Terminate''')
        self.speak("Powering ON")

    def text_box_input(self):
        text_box_dialog = customtkinter.CTkInputDialog(text="Type in text:", title="Text Input")
        user = text_box_dialog.get_input()
        self.textbox.insert("end", f"\nUser said: {user}\n")
        return user

    def clear_text(self):
        self.textbox.delete('1.0', tk.END)
        self.textbox.insert("0.0", "Hii, I am your assistant what can I do For You")

    def correctS(self):
        input_text = self.takeCommand()
        self.textbox.insert("end", f"\nComputing...")
        if not self.muted:
            self.speak(f"Computing...")
        corrected_text_spell = self.correct_spelling(input_text)
        corrected_text_grammar = self.correct_grammar(corrected_text_spell)
        self.textbox.insert("end", f"\nCorrected sentence (spelling and grammar): {corrected_text_grammar}")
        if not self.muted:
            self.speak(f"Corrected sentence (spelling and grammar): {corrected_text_grammar}")

    def correctT(self):
        correct_text_dialog = customtkinter.CTkInputDialog(text="Type in text:", title="Grammer and Spell Checker")
        input_text = correct_text_dialog.get_input()
        self.textbox.insert("end", f"\nComputing...")
        if not self.muted:
            self.speak(f"Computing...")
        corrected_text_spell = self.correct_spelling(input_text)
        corrected_text_grammar = self.correct_grammar(corrected_text_spell)
        self.textbox.insert("end", f"\nCorrected sentence (spelling and grammar): {corrected_text_grammar}")
        if not self.muted:
            self.speak(f"Corrected sentence (spelling and grammar): {corrected_text_grammar}")

    def correct_spelling(self, text):
        spell = SpellChecker()
        words = text.split()
        corrected_words = []

        corrected_words = [spell.correction(word) for word in words]
        corrected_text = ' '.join(corrected_words)
        return corrected_text

    def correct_grammar(self, text):
        tool = language_tool_python.LanguageTool('en-IN')
        matches = tool.check(text)
        corrected_text = language_tool_python.utils.correct(text, matches)
        return corrected_text

    def save_text(self):
        text_dialog = customtkinter.CTkInputDialog(text="Type in text:", title="Name")
        self.text_to_speech(text_dialog.get_input())
        file_path = filedialog.asksaveasfilename(defaultextension=".mp3", filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")])
        if file_path:
            os.rename("corrected_pronunciation.mp3", file_path)
            self.textbox.insert("end", f"\nPronunciation saved successfully at: {file_path}")
        else:
            self.textbox.insert("end", "\nSave operation canceled.")

    def save_speach(self):
        recognized_text = self.takeCommand()
        self.text_to_speech(recognized_text)
        file_path = filedialog.asksaveasfilename(defaultextension=".mp3", filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")])
        if file_path:
            os.rename("corrected_pronunciation.mp3", file_path)
            self.textbox.insert("end", f"\nPronunciation saved successfully at: {file_path}")
        else:
            self.textbox.insert("end", "\nSave operation canceled.")

    def text_to_speech(self, text):
        tts = gTTS(text)
        tts.save("corrected_pronunciation.mp3")
        os.system("corrected_pronunciation.mp3")

    def text_input_toggle(self):
        self.text_input = not self.text_input
        if self.text_input:
            self.textbox.insert("end", f"\nText input enabled")
            if not self.muted:
                self.speak(f"Text input enabled")
        else:
            self.textbox.insert("end", f"\nText input disabled")
            if not self.muted:
                self.speak(f"Text input disabled")

    def mute(self):
        self.muted = not self.muted
        if self.muted:
            self.engine.setProperty('volume', 0)  # Mute the speech engine
        else:
            self.engine.setProperty('volume', 1)  # Unmute the speech engine

    def add_contact(self):
        flag = 0
        self.name = self.name_entry.get().lower()
        self.number = self.number_entry.get()
        self.name_entry.delete(0, 'end')
        self.number_entry.delete(0, 'end')
        with open('contacts.txt', 'r') as file:
            current_content = file.readlines()
            for index, line in enumerate(current_content):
                if self.name in line.lower():
                    flag = 1
                    self.textbox.insert("end", f"\n{self.name} is not added to contacts as it already exists")
                    if not self.muted:
                        self.speak(f"{self.name} is not added to contacts as it already exists")
                    break
        if (flag == 0):
            try:
                with open("contacts.txt", "a") as file:
                    file.write(f"{self.name.lower()}:{int(self.number)}\n")
                self.contacts.clear()
                with open("contacts.txt", "r") as file:
                    for line in file:
                        name, phone_number = line.strip().split(':')
                        self.contacts[name] = phone_number
                self.textbox.insert("end", f"\n{self.name} has been successfully added to the Contacts.")
                if not self.muted:
                    self.speak(f"{self.name} has been successfully added to the Contacts.")
            except Exception as e:
                self.textbox.insert("end", f"\nError, An error occurred: {str(e)}")

    def show_contacts(self):
        contacts_popup = Toplevel(self.master)
        contacts_popup.title("Contacts")
        contacts_popup.configure(bg='black')

        # Read content from the text file
        with open('contacts.txt', 'r') as file:
            contacts = file.read()

        # Display file content using CtLabel widget
        contacts_label = customtkinter.CTkLabel(contacts_popup, text=contacts)
        contacts_label.pack()

    def delete_contact(self):
        line_number = None
        text_to_delete = self.delete_entry.get().lower()
        self.delete_entry.delete(0, 'end')
        with open('contacts.txt', 'r') as file:
            current_content = file.readlines()
            for index, line in enumerate(current_content):
                if text_to_delete in line.lower():
                    line_number = index
                    break
        if line_number is not None:
            del current_content[line_number]
            with open("contacts.txt", "w") as file:
                file.writelines(current_content)
            self.contacts.clear()
            with open("contacts.txt", "r") as file:
                for line in file:
                    name, phone_number = line.strip().split(':')
                    self.contacts[name] = phone_number
            self.textbox.insert("end", f"\n{text_to_delete} has been successfully deleted from the Contacts.")
            if not self.muted:
                self.speak(f"{text_to_delete} has been successfully deleted from the Contacts.")
        else:
            self.textbox.insert("end", "\nContact not found")
            if not self.muted:
                self.speak("Contact not found")

    def change_language(self, new_language: str):
        global language
        if(new_language == "Hindi"):
            language = 'hi-IN'
        if(new_language == "English"):
            language = 'en-IN'
        if(new_language == "Japanese"):
            language = 'ja'
        if(new_language == "French"):
            language = 'fr'
        if(new_language == "German"):
            language = 'de'
        if(new_language == "Spanish"):
            language = 'es'

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def save_to_file(self):
        self.data = self.entry.get()  # Get input from the entry widget
        self.entry.delete(0, 'end')
        try:
            with open("Feedback.txt", "a") as file:
                file.write(f"{self.data}\n\n")
            self.textbox.insert("end", f"\nThanks for the Feedback")
            if not self.muted:
                self.speak("Thanks for the Feedback")
        except Exception as e:
            self.textbox.insert("end", f"\nError An error occurred: {str(e)}")

    def set_volume(self, volume_level):
        try:
            self.volume_level = self.slider_1.get()
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMasterVolumeLevelScalar(self.volume_level, None)
            self.update_volume_label()
        except Exception as e:
            self.textbox.insert("end", f"\nError An error occurred: {str(e)}")
    
    def update_volume_label(self):
        self.volume_label.configure(text=f"Volume: {int(self.volume_level * 100)}")

    def query(self, user_query):
        flag = 0
        URL = "https://www.google.co.in/search?q=" + user_query

        headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
        }

        page = requests.get(URL, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        try:
            result = soup.find(class_='Z0LcW t2b5Cf').get_text()
        except Exception as e:
            flag = 1
        if flag == 1:
            flag = 0
            try:
                result = soup.find(class_='hgKElc').get_text()
            except Exception as e:
                flag = 1
        if flag == 1:
            flag = 0
            try:
                result = soup.find(class_='wHYlTd sY7ric').get_text()
            except Exception as e:
                flag = 1
        self.textbox.insert("end", f"\n{result}")
        if not self.muted:
            self.speak(result)

    def search(self, user_input):
        user_query = user_input
        try:
            self.query(user_query)
        except Exception as e:
            self.textbox.insert("end", "\nI can search that on google for you")
            self.textbox.insert("end", "\nsay Proceed to continue")
            if not self.muted:
                self.speak("I can search that on google for you")
                self.speak("say Proceed to continue")
            if not self.text_input:
                if(self.takeCommand().lower() == "proceed"):
                    user_input = user_input.replace("google search", "")
                    words = user_input.split()
                    search = 'https://www.google.com/search?q='
                    for word in words:
                        search += (str(word)) + '+'
                    webbrowser.open(search)
                else:
                    self.textbox.insert("end", "\nOk")
                    if not self.muted:
                        self.speak("Ok")
            else:
                if(self.text_box_input().lower() == "proceed"):
                    user_input = user_input.replace("google search", "")
                    words = user_input.split()
                    search = 'https://www.google.com/search?q='
                    for word in words:
                        search += (str(word)) + '+'
                    webbrowser.open(search)
                else:
                    self.textbox.insert("end", "\nOk")
                    if not self.muted:
                        self.speak("Ok")
                

    # Function to make the Assistant speak
    def speak(self, audio):
        self.engine.say(audio)
        self.engine.runAndWait()

    # Function to take command from the user using speech recognition
    def takeCommand(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            self.textbox.insert("end", "\nListening...")
            if not self.muted:
                self.speak("Listening...")
            r.pause_threshold = 1
            audio = r.listen(source)
        try:
            self.textbox.insert("end", "\nRecognizing...")
            if not self.muted:
                self.speak("Recognizing...")
            query = r.recognize_google(audio, language = language)
            self.textbox.insert("end", f"\nUser said: {query}\n")
        except Exception as e:
            self.textbox.insert("end", "\nSpeach did't recognized")
            if not self.muted:
                self.speak("Speach did't recognized")
            return "None"
        return query

    def call(self):
        if not self.text_input:
            user_input = self.takeCommand()
        else:
            user_input = self.text_box_input()
        euser_input = user_input.lower()
        if 'रद्द करें' in user_input:
            self.textbox.insert("end", "\nअलविदा!")
            if not self.muted:
                self.speak("अलविदा!")
            return 0
        elif 'यूट्यूब पर' in user_input or 'यूट्यूब खोलें' in user_input:
            if user_input == 'यूट्यूब खोलें':
                webbrowser.open('https://www.youtube.com/')
            elif 'यूट्यूब पर' in user_input:
                user_input = user_input.replace("यूट्यूब पर", "")
                user_input = user_input.replace("सर्च करें", "")
                pywhatkit.playonyt(user_input)
            else:
                words = user_input.split()
                search = 'https://www.youtube.com/results?search_query='
                for word in words:
                    search += (str(word)) + '+'
                webbrowser.open(search)
        elif 'गूगल खोलें' in user_input or 'गूगल सर्च' in user_input or 'गूगल पर' in user_input:
            if user_input == 'गूगल खोलें':
                webbrowser.open('https://www.google.com')
            else:
                user_input = user_input.replace("गूगल सर्च", "")
                user_input = user_input.replace("गूगल पर", "")
                user_input = user_input.replace("सर्च करें", "")
                words = user_input.split()
                search = 'https://www.google.com/search?q='
                for word in words:
                    search += (str(word)) + '+'
                webbrowser.open(search)
        elif 'लिखित में ले' in user_input:
            dialog_box = customtkinter.CTkInputDialog(text="पाठ दर्ज करें", title="लिखो")
            self.search(dialog_box.get_input())
        elif 'बस लिखो' in euser_input:
            if not self.text_input:
                self.takeCommand()
            else:
                self.text_box_input()
        elif 'terminate' in euser_input:
            self.textbox.insert("end", "\nGoodbye!")
            if not self.muted:
                self.speak("Goodbye!")
            return 0
        elif 'wikipedia' in euser_input:
            if not self.muted:
                self.speak('Searching Wikipedia...')
            euser_input = euser_input.replace("wikipedia", "")
            results = wikipedia.summary(euser_input, sentences=2)
            if not self.muted:
                self.speak("According to Wikipedia")
            self.textbox.insert("end", f"\n {results}")
            if not self.muted:
                self.speak(results)
        elif 'open youtube' in euser_input or 'search youtube' in euser_input or 'on youtube'in euser_input:
            if euser_input == 'open youtube':
                webbrowser.open('https://www.youtube.com/')
            elif 'on youtube' in euser_input:
                euser_input = euser_input.replace("play", "")
                euser_input = euser_input.replace("on youtube", "")
                pywhatkit.playonyt(euser_input)
            else:
                euser_input = euser_input.replace("search youtube", "")
                words = euser_input.split()
                search = 'https://www.youtube.com/results?search_query='
                for word in words:
                    search += (str(word)) + '+'
                webbrowser.open(search)
        elif 'open google' in euser_input or 'google search' in euser_input:
            if euser_input == 'open google':
                webbrowser.open('https://www.google.com')
            else:
                euser_input = euser_input.replace("google search", "")
                words = euser_input.split()
                search = 'https://www.google.com/search?q='
                for word in words:
                    search += (str(word)) + '+'
                webbrowser.open(search)
        elif 'send message' in euser_input:
            self.textbox.insert("end", "\nTo whom you want to send message")
            if not self.muted:
                self.speak("To whom you want to send message")
            if not self.text_input:
                number = self.takeCommand().lower()
            else:
                number = self.text_box_input().lower()
            for name in self.contacts:
                if number == name:
                    number = self.contacts[name]
            number = '+91' + number
            try:
                num = int(number)
            except Exception:
                self.textbox.insert("end", "\nInvalid Number")
                if not self.muted:
                    self.speak("Invalid Number")
                return -1
            self.textbox.insert("end", "\nWhat message do you want to send")
            if not self.muted:
                self.speak("What message do you want to send")
            if not self.text_input:
                message = self.takeCommand().lower()
            else:
                message = self.text_box_input().lower()
            pywhatkit.sendwhatmsg_instantly(number, message, 15, True, 30)
            self.textbox.insert("end", "\nMessage sent Successfully")
            if not self.muted:
                self.speak("Message sent Successfully")
        elif 'pronounce' in euser_input:
            euser_input = euser_input.replace("pronounce", "")
            self.textbox.insert("end", f"\nAssistant: {euser_input}")
            if not self.muted:
                self.speak(euser_input)
        elif 'take text input' in euser_input:
            self.textbox.insert("end", f"\nAssistant: {euser_input}")
            dialog_box = customtkinter.CTkInputDialog(text="Enter text", title="Text Input")
            self.search(dialog_box.get_input())
        elif 'just type' in euser_input:
            self.textbox.insert("end", f"\nAssistant: {euser_input}")
            if not self.text_input:
                self.takeCommand()
            else:
                self.text_box_input()
        else:
            try:
                user_input = user_input.lower()
                self.search(user_input)
            except Exception as e:
                self.textbox.insert("end", f"\nError An error occurred: {str(e)}")

    def start_thread(self, target):
        # Making Threads
        thread = threading.Thread(target=target)
        thread.start()

    def calling(self):
        self.start_thread(self.call)

    def adding(self):
        self.start_thread(self.add_contact)

    def deleting(self):
        self.start_thread(self.delete_contact)
    
    def saving_speach(self):
        self.start_thread(self.save_speach)

    def saving_text(self):
        self.start_thread(self.save_text)

    def correct_speach(self):
        self.start_thread(self.correctS)
        
    def correct_text(self):
        self.start_thread(self.correctT)

    def toggling(self):
        self.start_thread(self.text_input_toggle)
    
    def Saving_to_file(self):
        self.start_thread(self.save_to_file)

if __name__ == "__main__":
    app = App()
    app.mainloop()