import threading
import queue
import datetime
import webbrowser
import tkinter as tk
from tkinter import scrolledtext, messagebox
import speech_recognition as sr # type: ignore
import pyttsx3 # type: ignore
import requests # type: ignore

OPENWEATHER_API_KEY = ""  # Add your OpenWeather API key if needed


# -------------- Helper classes / functions --------------
class VoiceAssistant:
    """Core assistant logic separate from GUI so it's easy to reuse/test."""

    def __init__(self):
        # Text-to-speech engine
        self.tts = pyttsx3.init()
        self.tts.setProperty("rate", 165)
        self.tts.setProperty("volume", 1.0)

    def speak(self, text):
        """Speak text (non-blocking using a thread to keep GUI responsive)."""

        def _speak():
            try:
                self.tts.say(text)
                self.tts.runAndWait()
            except Exception as e:
                print("TTS error:", e)

        t = threading.Thread(target=_speak, daemon=True)
        t.start()

    def handle_query(self, text):
        """Return a string reply based on the recognized text."""
        text = text.strip().lower()
        if not text:
            return "I didn't catch anything."

        if "hello" in text or "hi" in text or "hey" in text:
            return "Hello! How can I assist you today?"

        if "time" in text:
            now = datetime.datetime.now().strftime("%I:%M %p")
            return f"The current time is {now}."

        if text.startswith("search "):
            query = text[len("search "):].strip()
            if query:
                url = "https://www.google.com/search?q=" + query.replace(" ", "+")
                webbrowser.open(url)
                return f"Searching the web for {query}."
            return "What would you like me to search for?"

        if text.startswith("weather "):
            if not OPENWEATHER_API_KEY:
                return "Weather feature is not configured. Add an API key to enable this."
            city = text[len("weather "):].strip()
            if not city:
                return "Please tell me the city name for the weather."
            return self._get_weather_for_city(city)

        if text.startswith("remind me to "):
            return "Reminder noted: " + text[len("remind me to "):]

        return "Sorry, I don't know how to do that yet. Try asking for the time, searching, or saying hello."

    def _get_weather_for_city(self, city):
        """Call OpenWeatherMap to get a short weather summary."""
        try:
            base = "https://api.openweathermap.org/data/2.5/weather"
            params = {"q": city, "appid": OPENWEATHER_API_KEY, "units": "metric"}
            resp = requests.get(base, params=params, timeout=7)
            resp.raise_for_status()
            data = resp.json()
            desc = data["weather"][0]["description"].capitalize()
            temp = data["main"]["temp"]
            return f"Weather in {city}: {desc}, {temp}°C."
        except Exception as e:
            print("Weather error:", e)
            return "Couldn't fetch weather right now. Please check your API key and network."


# -------------- GUI --------------
class VoiceAssistantGUI(tk.Tk):
    def __init__(self, assistant):
        super().__init__()
        self.assistant = assistant
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.listening = False
        self.audio_queue = queue.Queue()

        self.title("Python Voice Assistant")
        self.geometry("640x420")
        self.configure(padx=10, pady=10)

        lbl = tk.Label(self, text="Python Voice Assistant", font=("Segoe UI", 18, "bold"))
        lbl.pack(pady=(0, 6))

        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True)

        self.txt_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=12)
        self.txt_area.pack(fill="both", expand=True)
        self.txt_area.configure(state="disabled", font=("Segoe UI", 10))

        controls = tk.Frame(self)
        controls.pack(fill="x", pady=(8, 0))

        self.btn_listen = tk.Button(controls, text="Start Listening", command=self.toggle_listen, width=16)
        self.btn_listen.pack(side="left", padx=(0, 8))

        self.btn_test = tk.Button(controls, text="Type & Ask", command=self.ask_typed)
        self.btn_test.pack(side="left", padx=(0, 8))

        self.entry = tk.Entry(controls)
        self.entry.pack(side="left", fill="x", expand=True)

        self._init_microphone()

        self.stop_flag = threading.Event()
        self.process_thread = threading.Thread(target=self._process_queue_loop, daemon=True)
        self.process_thread.start()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _init_microphone(self):
        try:
            self.microphone = sr.Microphone()
        except Exception as e:
            print("Microphone init failed:", e)
            self.microphone = None
            self.btn_listen.configure(state="disabled")
            messagebox.showwarning("Microphone", "No microphone found or PyAudio not installed. Listening disabled.")

    def toggle_listen(self):
        if not self.listening:
            self.start_listening()
        else:
            self.stop_listening()

    def start_listening(self):
        if not self.microphone:
            messagebox.showerror("Error", "Microphone not available.")
            return

        self.listening = True
        self.btn_listen.configure(text="Stop Listening")
        try:
            self.stop_listening_fn = self.recognizer.listen_in_background(self.microphone, self._callback)
            self._append_text("Assistant: Listening started...\n")
        except Exception as e:
            messagebox.showerror("Error starting listening", str(e))
            self.listening = False
            self.btn_listen.configure(text="Start Listening")

    def stop_listening(self):
        if hasattr(self, "stop_listening_fn") and callable(self.stop_listening_fn):
            self.stop_listening_fn(wait_for_stop=False)
        self.listening = False
        self.btn_listen.configure(text="Start Listening")
        self._append_text("Assistant: Listening stopped.\n")

    def _callback(self, recognizer, audio):
        self.audio_queue.put(audio)

    def _process_queue_loop(self):
        while not self.stop_flag.is_set():
            try:
                audio = self.audio_queue.get(timeout=0.5)
            except queue.Empty:
                continue
            t = threading.Thread(target=self._recognize_and_respond, args=(audio,), daemon=True)
            t.start()

    def _recognize_and_respond(self, audio):
        try:
            text = self.recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            text = ""
        except sr.RequestError as e:
            text = ""
            print("Speech recognition request failed:", e)

        if text:
            self._append_text("You: " + text + "\n")
            response = self.assistant.handle_query(text)
            self._append_text("Assistant: " + response + "\n\n")
            self.assistant.speak(response)
        else:
            self._append_text("Assistant: Sorry, I couldn't understand.\n")

    def ask_typed(self):
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, tk.END)
        self._append_text("You (typed): " + text + "\n")
        response = self.assistant.handle_query(text)
        self._append_text("Assistant: " + response + "\n\n")
        self.assistant.speak(response)

    def _append_text(self, text):
        def _do():
            self.txt_area.configure(state="normal")
            self.txt_area.insert(tk.END, text)
            self.txt_area.see(tk.END)
            self.txt_area.configure(state="disabled")

        self.after(0, _do)

    def on_close(self):
        if self.listening:
            self.stop_listening()
        self.stop_flag.set()
        self.destroy()


# -------------- Entry point --------------
def main():
    assistant = VoiceAssistant()
    app = VoiceAssistantGUI(assistant)
    app.mainloop()


if __name__ == "__main__":
    main()
