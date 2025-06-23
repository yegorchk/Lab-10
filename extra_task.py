import json, time, requests, webbrowser
import pyttsx3, pyaudio, vosk

class Speech:
    def __init__(self):
        self.tts = pyttsx3.init('sapi5')
    def set_voice(self, speaker):
        voices = self.tts.getProperty('voices')
        return voices[speaker].id
    def text2voice(self, speaker=0, text='Ready'):
        self.tts.setProperty('voice', self.set_voice(speaker))
        self.tts.say(text)
        self.tts.runAndWait()

class Recognize:
    def __init__(self, lang='en'):
        model = vosk.Model('model_small_en')
        self.record = vosk.KaldiRecognizer(model, 16000)
        self.stream()

    def stream(self):
        pa = pyaudio.PyAudio()
        self.stream = pa.open(format=pyaudio.paInt16, channels=1, rate=16000,
                              input=True, frames_per_buffer=8000)

    def listen(self):
        while True:
            data = self.stream.read(4000, exception_on_overflow=False)
            if self.record.AcceptWaveform(data) and len(data) > 0:
                answer = json.loads(self.record.Result())
                if answer['text']:
                    yield answer['text']

def get_word_info(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    r = requests.get(url)
    if r.ok:
        return r.json()
    return None

def speak(text):
    speech = Speech()
    speech.text2voice(speaker=1, text=text)

def handle_command(text, context):
    if text.startswith("find "):
        word = text.split("find ", 1)[1].strip()
        info = get_word_info(word)
        if info:
            context['info'] = info
            context['word'] = word
            speak(f"Found {word}")
        else:
            speak("Word not found.")
    elif text == "meaning" and context.get('info'):
        meaning = context['info'][0]['meanings'][0]['definitions'][0]['definition']
        speak(meaning)
    elif text == "example" and context.get('info'):
        example = context['info'][0]['meanings'][0]['definitions'][0].get('example')
        if example:
            speak(example)
        else:
            speak("No example available.")
    elif text == "save" and context.get('info') and context.get('word'):
        with open(f"{context['word']}.txt", "w") as f:
            f.write(json.dumps(context['info'], indent=2))
        speak("Saved to file.")
    elif text == "link" and context.get('word'):
        url = f"https://dictionary.cambridge.org/dictionary/english/{context['word']}"
        webbrowser.open(url)
        speak("Opened in browser.")
    elif text in ("close", "exit", "quit"):
        speak("Goodbye!")
        return False
    else:
        speak("Unknown command.")
    return True

if __name__ == "__main__":
    context = {}
    rec = Recognize(lang='en')
    text_gen = rec.listen()
    rec.stream.stop_stream()
    speak("Dictionary assistant started.")
    time.sleep(0.5)
    rec.stream.start_stream()
    for text in text_gen:
        print(f"Recognized: {text}")
        if not handle_command(text, context):
            break