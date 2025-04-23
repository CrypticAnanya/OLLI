import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
from PIL import Image, ImageTk
import datetime
import os
import sys
import datetime
from time import strftime
import pytz
import speech_recognition as sr
import os
import pyttsx3
import webbrowser
import openai
import threading
import pyaudio
searching = True
listening_for_interrupt = False
stop_speaking = False
expecting_code = False
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class JARVISUI:
    def __init__(self, master):
        self.master = master
        master.title("JARVIS AI Assistant")
        master.attributes("-fullscreen","True")
        master.configure(bg='#0a192f')  # Dark blue background

        # Set window icon
        try:
            #icon_path = self.resource_path('jarvis_icon.ico')
            master.iconbitmap(default=icon_path)
        except Exception as e:
            print(f"Icon error: {e}")

        # Custom styling
        self.style = ttk.Style()
        self.style.theme_use('clam')  # More modern theme that supports customization

        # Configure styles
        self.style.configure('TFrame', background='#0a192f')
        self.style.configure('TLabel', background='#0a192f', foreground='white')
        self.style.configure('TButton',
                             font=('Helvetica', 10, 'bold'),
                             background='#1e3d59',
                             foreground='white',
                             borderwidth=1,
                             padding=5)
        self.style.map('TButton',
                       background=[('active', '#3a7ca5'), ('!active', '#1e3d59')],
                       foreground=[('active', 'white'), ('!active', 'white')])

        # Header Frame
        self.header_frame = ttk.Frame(master)
        self.header_frame.pack(fill=tk.X, padx=10, pady=10)

        # Logo
        '''try:
            logo_path = self.resource_path('jarvis_logo.png')
            self.logo_img = Image.open(logo_path)
            self.logo_img = self.logo_img.resize((60, 60), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(self.logo_img)
            self.logo_label = ttk.Label(self.header_frame, image=self.logo_photo, background='#0a192f')
            self.logo_label.grid(row=0, column=0, padx=(0, 10))
        except Exception as e:
            print(f"Logo error: {e}")
            self.logo_label = ttk.Label(self.header_frame, text="JARVIS",
                                        font=('Helvetica', 24, 'bold'),
                                        foreground='#64ffda',
                                        background='#0a192f')
            self.logo_label.grid(row=0, column=0, padx=(0, 10))'''

        # Title and status
        self.title_label = ttk.Label(self.header_frame,
                                     text="JARVIS AI Assistant",
                                     font=('Helvetica', 20, 'bold'),
                                     foreground='white',
                                     background='#0a192f')
        self.title_label.grid(row=0, column=1, sticky='w')

        self.status_label = ttk.Label(self.header_frame,
                                      text="Status: Ready",
                                      font=('Helvetica', 10),
                                      foreground='#64ffda',
                                      background='#0a192f')
        self.status_label.grid(row=1, column=1, sticky='w', pady=(5, 0))

        # Main content frame
        self.main_frame = ttk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Conversation display
        self.conversation_text = scrolledtext.ScrolledText(
            self.main_frame,
            wrap=tk.WORD,
            font=('Helvetica', 10),
            bg='#172a45',
            fg='white',
            insertbackground='white',
            padx=10,
            pady=10,
            state='disabled'
        )
        self.conversation_text.pack(fill=tk.BOTH, expand=True)

        # Input frame
        self.input_frame = ttk.Frame(master)
        self.input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        # Input field
        self.input_entry = ttk.Entry(
            self.input_frame,
            font=('Helvetica', 12)
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.input_entry.bind('<Return>', self.process_input)
        self.input_entry.focus_set()

        # Buttons
        self.button_frame = ttk.Frame(self.input_frame)
        self.button_frame.pack(side=tk.RIGHT)

        self.listen_btn = ttk.Button(
            self.button_frame,
            text="🎤 Listen",
            command=self.start_listening,
            width=10
        )
        self.listen_btn.pack(side=tk.LEFT, padx=2)

        self.send_btn = ttk.Button(
            self.button_frame,
            text="Send",
            command=self.process_input,
            width=8
        )
        self.send_btn.pack(side=tk.LEFT, padx=2)

        # Control buttons frame
        self.control_frame = ttk.Frame(master)
        self.control_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        buttons = [
            ("✉️ Email", self.open_email_dialog),
            ("</> Code", self.open_code_dialog),
            ("⚙ Settings", self.open_settings),
            ("❌ Exit", master.quit)
        ]

        for i, (text, command) in enumerate(buttons):
            btn = ttk.Button(
                self.control_frame,
                text=text,
                command=command,
                width=10
            )
            if i == len(buttons) - 1:  # Last button (Exit)
                btn.pack(side=tk.RIGHT, padx=2)
            else:
                btn.pack(side=tk.LEFT, padx=2)

        # Initialize conversation
        self.add_to_conversation("JARVIS", "Hello, my name is JARVIS. How can I assist you today?")

        # Initialize voice recognition
        self.listening_thread = None
        self.listening_active = False

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def add_to_conversation(self, sender, message):
        self.conversation_text.configure(state='normal')
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.conversation_text.insert(tk.END, f"[{timestamp}] {sender}: {message}\n")
        self.conversation_text.configure(state='disabled')
        self.conversation_text.see(tk.END)

    def process_input(self, event=None):
        user_input = self.input_entry.get().strip()
        if not user_input:
            return

        self.add_to_conversation("You", user_input)
        self.input_entry.delete(0, tk.END)

        # Process the command in a separate thread
        threading.Thread(
            target=self.process_command,
            args=(user_input,),
            daemon=True
        ).start()

    def process_command(self, command):
        self.update_status("Processing...")

        try:
            # Here you would integrate with your existing command processing logic
            # For now simulating a response
            response = f"I received your command: {command}"

            self.master.after(0, lambda: self.add_to_conversation("JARVIS", response))
        except Exception as e:
            error_msg = f"Error processing command: {str(e)}"
            self.master.after(0, lambda: self.add_to_conversation("JARVIS", error_msg))
        finally:
            self.update_status("Ready")

    def update_status(self, text):
        self.master.after(0, lambda: self.status_label.config(text=f"Status: {text}"))

    def start_listening(self):
        def say(text):
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        def takecommand():
            r = sr.Recognizer()
            return r
        with sr.Microphone() as source:
            r=takecommand()
            r.pause_threshold = 1
            try:
                self.add_to_conversation("You","Listening for your command...")
                audio = r.listen(source)
                print("Recognizing...")
                query = r.recognize_google(audio, language="en-in")
                print(f"User said: {query}")
                return query
            except sr.RequestError:
                error_msg = "Error: Unable to connect to the speech recognition service. Please check your internet connection."
                print(error_msg)
                say(error_msg)
                return error_msg
            except sr.UnknownValueError:
                error_msg = "Sorry, I couldn't understand what you said. Please try speaking again."
                print(error_msg)
                say(error_msg)
                return error_msg
            except Exception as e:
                error_msg = f"An unexpected error occurred: {str(e)}"
                print(error_msg)
                say("An error occurred while listening. Please try again.")
                return error_msg
        
        say("Hello My name is JARVIS")
        while True:
            print("Listening.....")
            query = takecommand()
            if "i want to type" in query.lower():
                say("Okay, switching to text mode. Please type your command.")
                query = input("Enter your command: ")
            if expecting_code:
                if "type" in query.lower():
                    say("Paste your code. Type 'done' on a new line when you're finished.")
                    code_lines = []
                    while True:
                        line = input()
                        if line.strip().lower() == "done":
                            break
                        code_lines.append(line)
                        full_code = "\n".join(code_lines)
                else:
                    say("Please start giving your code. Say 'done' when you are finished.")
                    code_lines = []
                    while True:
                        line = takecommand()
                        if "done" in line.lower():
                            break
                    # Replace voice-format terms
                    line = line.replace("colon", ":").replace("indent", "    ").replace("open parenthesis",
                                                                                        "(").replace(
                        "close parenthesis", ")")
                    code_lines.append(line)
                full_code = "\n".join(code_lines)
            corrected_code = ai(f"Please correct the following Python code:\n\n{full_code}")
            say("Here's the corrected version.")
            print("Corrected Code:\n", corrected_code)
            expecting_code = False
            continue
            
        # if not self.listening_active:
        #     self.listening_active = True
        #     self.listen_btn.config(text="🔴 Listening...")
        #     self.update_status("Listening...")

        #     # Start listening in a separate thread
        #     self.listening_thread = threading.Thread(
        #         target=self.listen_for_speech,
        #         daemon=True
        #     )
        #     self.listening_thread.start()
        # else:
        #     self.stop_listening()

    def stop_listening(self):
        self.listening_active = False
        self.listen_btn.config(text="🎤 Listen")
        self.update_status("Ready")

    def listen_for_speech(self):
        # Here you would integrate with your speech recognition code
        import time
        import random

        while self.listening_active:
            time.sleep(2)  # Simulate listening time

            # Simulate recognized speech
            phrases = [
                "What's the weather today?",
                "Open Google for me",
                "What time is it?",
                "Send an email to John",
                "Correct my Python code"
            ]
            simulated_input = random.choice(phrases)

            self.master.after(0, lambda: [
                self.add_to_conversation("You (Voice)", simulated_input),
                self.process_command(simulated_input),
                self.stop_listening() if random.random() > 0.7 else None
            ])

    def open_email_dialog(self):
        email_window = tk.Toplevel(self.master)
        email_window.title("Compose Email")
        email_window.geometry("500x400")
        email_window.configure(bg='#0a192f')
        email_window.transient(self.master)  # Set as child window
        email_window.grab_set()  # Make modal

        # Email form
        ttk.Label(email_window, text="To:").pack(pady=(10, 0))
        to_entry = ttk.Entry(email_window, width=50)
        to_entry.pack(pady=(0, 10))

        ttk.Label(email_window, text="Subject:").pack()
        subject_entry = ttk.Entry(email_window, width=50)
        subject_entry.pack(pady=(0, 10))

        ttk.Label(email_window, text="Message:").pack()
        message_text = scrolledtext.ScrolledText(
            email_window,
            wrap=tk.WORD,
            width=50,
            height=10,
            font=('Helvetica', 10),
            bg='#172a45',
            fg='white'
        )
        message_text.pack(pady=(0, 10))

        button_frame = ttk.Frame(email_window)
        button_frame.pack(pady=10)

        ttk.Button(button_frame,
                   text="Cancel",
                   command=email_window.destroy).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame,
                   text="Send Email",
                   command=lambda: self.send_email_action(
                       to_entry.get(),
                       subject_entry.get(),
                       message_text.get("1.0", tk.END),
                       email_window
                   )).pack(side=tk.RIGHT, padx=5)

    def send_email_action(self, to, subject, message, window):
        if not to or not subject or not message.strip():
            self.add_to_conversation("JARVIS", "Please fill all email fields")
            return

        # Here you would call your actual email sending function
        self.add_to_conversation("JARVIS",
                                 f"Preparing to send email to {to} with subject '{subject}'")
        window.destroy()

    def open_code_dialog(self):
        code_window = tk.Toplevel(self.master)
        code_window.title("Code Correction")
        code_window.geometry("600x500")
        code_window.configure(bg='#0a192f')
        code_window.transient(self.master)
        code_window.grab_set()

        ttk.Label(code_window,
                  text="Enter your code for correction:").pack(pady=(10, 0))

        code_text = scrolledtext.ScrolledText(
            code_window,
            wrap=tk.WORD,
            font=('Consolas', 10),
            bg='#172a45',
            fg='white',
            height=20
        )
        code_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        button_frame = ttk.Frame(code_window)
        button_frame.pack(pady=(0, 10))

        ttk.Button(button_frame,
                   text="Cancel",
                   command=code_window.destroy).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame,
                   text="Submit Code",
                   command=lambda: self.submit_code_action(
                       code_text.get("1.0", tk.END),
                       code_window
                   )).pack(side=tk.RIGHT, padx=5)

    def submit_code_action(self, code, window):
        if not code.strip():
            self.add_to_conversation("JARVIS", "Please enter some code")
            return

        # Here you would call your actual code correction function
        self.add_to_conversation("JARVIS", "Processing your code...")
        window.destroy()

    def open_settings(self):
        settings_window = tk.Toplevel(self.master)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.configure(bg='#0a192f')
        settings_window.transient(self.master)
        settings_window.grab_set()

        ttk.Label(settings_window,
                  text="JARVIS Settings",
                  font=('Helvetica', 14, 'bold')).pack(pady=10)

        # Voice settings
        voice_frame = ttk.Frame(settings_window)
        voice_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Label(voice_frame, text="Voice Speed:").pack(anchor='w')
        self.speed_var = tk.IntVar(value=200)
        ttk.Scale(voice_frame,
                  from_=100,
                  to=300,
                  variable=self.speed_var).pack(fill=tk.X)

        # Theme settings
        theme_frame = ttk.Frame(settings_window)
        theme_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Label(theme_frame, text="Theme:").pack(anchor='w')

        self.theme_var = tk.StringVar(value="dark")
        ttk.Radiobutton(theme_frame,
                        text="Dark",
                        variable=self.theme_var,
                        value="dark").pack(anchor='w')
        ttk.Radiobutton(theme_frame,
                        text="Light",
                        variable=self.theme_var,
                        value="light").pack(anchor='w')

        button_frame = ttk.Frame(settings_window)
        button_frame.pack(pady=20)

        ttk.Button(button_frame,
                   text="Cancel",
                   command=settings_window.destroy).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame,
                   text="Save",
                   command=lambda: self.save_settings_action(settings_window)).pack(side=tk.RIGHT, padx=5)

    def save_settings_action(self, window):
        self.add_to_conversation("JARVIS",
                                 f"Settings saved: Voice speed {self.speed_var.get()}, Theme {self.theme_var.get()}")
        window.destroy()


def main():
    root = tk.Tk()
    try:
        app = JARVISUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Application error: {e}")
        root.destroy()


if __name__ == "__main__":
    main()