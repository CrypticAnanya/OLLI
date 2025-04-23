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

def send_email(subject, body, to_email):
    from_email = "gppg317@gmail.com"
    password = "AGboy@@2001"  # Use app-specific password for Gmail

    message = MIMEMultipart()
    message["From"] = from_email
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, password)
        server.sendmail(from_email, to_email, message.as_string())
        server.quit()
        say("Email has been sent successfully.")
        print("Email sent!")
    except Exception as e:
        say("Sorry, I was not able to send the email.")
        print("Email sending error:", e)


def ai(prompt):
    try:
        openai.api_key = "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"
        openai.api_base = "https://api.groq.com/openai/v1"
        model_name = "llama3-8b-8192"

        response = openai.ChatCompletion.create(
            model=model_name,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        reply = response['choices'][0]['message']['content']
        print("AI Response:", reply)
        return reply

    except Exception as e:
        print(f"AI Error: {e}")
        return "Sorry, I encountered an error processing your request."
def chat(prompt):
    global searching
    if not searching:
        return "Searching is currently paused. Say 'start searching' to resume."
    try:
        openai.api_key = "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"
        openai.api_base = "https://api.groq.com/openai/v1"
        model_name = "llama3-8b-8192"

        response = openai.ChatCompletion.create(
            model=model_name,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        reply = response['choices'][0]['message']['content']
        print("Chat Response:", reply)
        say(reply)
        return reply

    except Exception as e:
        error_msg = f"Sorry, I encountered an error: {str(e)}"
        say(error_msg)
        print(f"Chat Error: {e}")
        return error_msg

def say(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
def takecommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.pause_threshold = 1
        try:
            print("Listening for your command...")
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
def get_current_time():
    india = pytz.timezone('Asia/Kolkata')
    now = datetime.datetime.now(india)
    return now.strftime("%I:%M %p")
def get_current_date():
    india = pytz.timezone('Asia/Kolkata')
    today = datetime.datetime.now(india)
    return today.strftime("%A, %d %B %Y")
if __name__ == '__main__':
    say("Hello My name is JARVIS")
    print('JARVIS')
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
        if "correct my code" in query.lower():
            say("Okay, would you like to type or speak your code?")
            expecting_code = True
            continue
        print("Processing query:", query)
        if "stop searching" in query.lower():
            searching = False
            say("I've paused searching. Say 'start searching' when you want me to continue.")
            continue
        elif "start searching" in query.lower():
            searching = True
            say("I've resumed searching. How can I help you?")
            continue
        skip_processing = False
        sites = [["youtube", "https://youtube.com"], ["wikipedia", "https://www.wikipedia.com"],["google", "https://www.google.com"],["instagram", "https://www.instagram.com"],["telegram", "https://web.telegram.org/a/"],["whatsapp", "https://web.whatsapp.com/"], ["gmail", "https://mail.google.com/"]]
        for site in sites:
            if f"open {site[0]}" in query.lower():
                say(f"Starting {site[0]}, sir...")
                webbrowser.open(site[1])
                skip_processing = True
        apps = [["game", r'start "" "C:\Users\Public\Desktop\Grand Theft Auto V.lnk"'],["music", r'start "" "C:\Users\irsha\Music"'],["notepad", r'start "" "C:\Windows\notepad.exe"'],["gallery", r'start "" "C:\Users\irsha\OneDrive\Pictures"']]
        for app in apps:
            if f"open {app[0]}" in query.lower():
                say(f"Starting {app[0]}, sir...")
                os.system(app[1])
                skip_processing = True
        if "the time" in query.lower():
            current_time = get_current_time()
            say(f"Sir, the time is {current_time}")
            print(f"Current time: {current_time}")
            skip_processing = True
        if "the date" in query.lower():
            current_date = get_current_date()
            say(f"Sir, today is {current_date}")
            print(f"Current date: {current_date}")
            skip_processing = True

        if "write an email" in query.lower() or "send email" in query.lower():
            say("Who should I send the email to?")
            to_email = input("Receiver Email Address: ") 
            say("What is the subject of the email?")
            subject = takecommand()

            say("What should I write in the email?")
            body = takecommand()

            say("Should I make it more professional using AI?")
            confirmation = takecommand()

            if "yes" in confirmation.lower():
                prompt = f"Write a professional email with subject: '{subject}' and message: '{body}'"
                body = ai(prompt)
                print("AI-enhanced Email:\n", body)

            send_email(subject, body, to_email)
            continue

        if "exit" in query.lower() or "quit" in query.lower() or "good bye" in query.lower() or "bye" in query.lower():
            say("Goodbye sir!")
            print("JARVIS shutting down...")
            skip_processing = True
            break
        if skip_processing:
            continue
        print("Processing query:", query)
        if "using ai" in query.lower():
            response = ai(query)
            print("AI output:", response)
            say(response)
        elif searching:
            response = chat(query)
            print("Chat output:", response)
