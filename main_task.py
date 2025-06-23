import json, time, random, requests
import pyttsx3, pyaudio, vosk

class Speech:
    def __init__(self):
        self.tts = pyttsx3.init('nsss')

    def set_voice(self):
        voices = self.tts.getProperty('voices')
        for voice in voices:
            if 'ru' in str(voice.languages).lower():
                return voice.id
        return voices[0].id  

    def text2voice(self, text='Готов'):
        self.tts.setProperty('voice', self.set_voice())
        self.tts.say(text)
        self.tts.runAndWait()

class Recognize:
    def __init__(self, lang='ru'):
        model = vosk.Model('model_small_ru' if lang=='ru' else 'model_small_en')
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

def get_rates():
    url = "https://open.er-api.com/v6/latest/RUB"
    r = requests.get(url)
    return r.json()['rates']

def speak(text):
    speech = Speech()
    speech.text2voice(text=text)

def handle_command(text, rates):
    if "доллар" in text:
        speak(f"Курс рубля к доллару: {rates.get('USD', 0):.4f}")
    elif "евро" in text:
        speak(f"Курс рубля к евро: {rates.get('EUR', 0):.4f}")
    elif "количество" in text:
        speak(f"Количество валют: {len(rates)}")
    elif "случайный" in text:
        code = random.choice(list(rates))
        speak(f"Курс рубля к {code}: {rates[code]:.4f}")
    elif "сохранить" in text:
        with open('rates.txt', 'w') as f:
            for k, v in rates.items():
                f.write(f'{k}: {v}\n')
        speak("Курсы сохранены в файл.")
    elif "закрыть" in text:
        speak("Пока! Хорошего дня.")
        return False
    return True

if __name__ == "__main__":
    rates = get_rates()
    rec = Recognize(lang='ru')
    text_gen = rec.listen()
    rec.stream.stop_stream()
    speak("Ассистент по курсам валют запущен.")
    time.sleep(0.5)
    rec.stream.start_stream()
    for text in text_gen:
        print(f"Распознано: {text}")
        if not handle_command(text, rates):
            break