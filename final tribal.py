import speech_recognition as sr
import pyttsx3
from googletrans import Translator
from twilio.rest import Client
import tkinter as tk
from tkinter import scrolledtext
import threading

# Initialize recognizer, translator, and text-to-speech engine
r = sr.Recognizer()
translator = Translator(service_urls=['translate.google.com'])


tts = pyttsx3.init()

# Twilio credentials
TWILIO_ACCOUNT_SID = 'AC4d10cc17317a6661ebf2f6145d0670a9'
TWILIO_AUTH_TOKEN = '38dc9966a117d14f847f8e7948f3de8c'
TWILIO_PHONE_NUMBER = '+18154539583'  # Ensure this is in E.164 format
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Helpline database (dictionary for demonstration purposes)
helpline_database = {
    "medical": '+919940625457',
    "fire": '+919940625457',
    "police": '+919940625457'
}

def find_helpline_number(keyword):
    if keyword.lower() in helpline_database:
        return helpline_database[keyword.lower()]
    return None

def update_ui(message, is_special=False):
    if is_special:
        # Display special message in larger text
        special_message_label.config(text=message)
        special_message_label.pack(pady=20)
        text_area.pack_forget()  # Hide text_area when showing special message
    else:
        special_message_label.pack_forget()  # Hide special message label
        text_area.insert(tk.END, message + "\n")
        text_area.yview(tk.END)

def recognition_thread():
    text = ""  # Initialize text with an empty string
    update_ui("Listening for speech...")

    while True:
        with sr.Microphone() as source:
            update_ui("Adjusting for ambient noise...")
            r.adjust_for_ambient_noise(source)
            update_ui("Listening...")
            audio = r.listen(source)

        try:
            # Recognize speech using Google Speech Recognition
            text = r.recognize_google(audio, language="sw")  # Use Swahili language code
            update_ui(f"Recognized text in Hmong: {text}")

            # Translate from Swahili to English
            translation = translator.translate(text, src='sw', dest='en')
            translated_text = translation.text
            update_ui(f"Translated to English: {translated_text}")
            tts.say(translated_text)
            tts.runAndWait()

            # Find helpline number based on the translated text
            helpline_number = find_helpline_number(translated_text)

            if helpline_number:
                if translated_text.lower() == "medical":
                    message = "Calling doctor"
                    is_special = False
                elif translated_text.lower() == "police":
                    message = "Calling police"
                    is_special = True  # Special case for police
                elif translated_text.lower() == "fire":
                    message = "Calling fire department"
                    is_special = False
                else:
                    message = f"Calling helpline number: {helpline_number}"
                    is_special = False

                update_ui(message, is_special)
                call = client.calls.create(
                    to=helpline_number,
                    from_=TWILIO_PHONE_NUMBER,
                    twiml=f'<Response><Say>Your request for {translated_text} has been received.</Say></Response>'
                )
                update_ui(f"Call initiated: {call.sid}")
            else:
                update_ui("No matching helpline found")

        except sr.UnknownValueError:
            update_ui("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            update_ui(f"Error with Google Speech Recognition service: {e}")
        except Exception as e:
            update_ui(f"An unexpected error occurred: {e}")

        # Optional: Exit condition
        if text.lower() == "stop":
            update_ui("Exiting...")
            break

# GUI setup
root = tk.Tk()
root.title("Voice Recognition and Helpline System")
root.geometry("700x600")  # Increased window size for more space
root.configure(bg='#D0F0C0')  # Light green background color

# Frame for UI components
frame = tk.Frame(root, bg='#F5F5DC', padx=15, pady=15)
frame.pack(padx=15, pady=15, fill=tk.BOTH, expand=True)

# Title label
title_label = tk.Label(frame, text="Voice Recognition and Helpline System", font=("Arial", 18, "bold"), bg='#F5F5DC', fg='#4B0082')
title_label.pack(pady=10)

# ScrolledText widget for displaying messages
text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=20, width=80, bg='#FAFAD2', font=("Arial", 12))
text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Special message label for larger text
special_message_label = tk.Label(frame, text="", font=("Arial", 24, "bold"), bg='#F5F5DC', fg='#FF0000')  # Red color for special messages

# Start button
start_button = tk.Button(frame, text="Start Recognition", font=("Arial", 14), bg='#32CD32', fg='white', relief=tk.RAISED, command=lambda: threading.Thread(target=recognition_thread, daemon=True).start())
start_button.pack(pady=10)

# Exit button
exit_button = tk.Button(frame, text="Exit", font=("Arial", 14), bg='#FF4500', fg='white', relief=tk.RAISED, command=root.quit)
exit_button.pack(pady=10)

root.mainloop()




















































































