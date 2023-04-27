import json, os

import pyttsx3, pyaudio, vosk

tts = pyttsx3.init('sapi5')

voices = tts.getProperty('voices')
tts.setProperty('voices', 'en')

for voice in voices:
    print(voice.name)
    if voice.name == 'Microsoft Zira Desktop - English (United States)':
        tts.setProperty('voice', voice.id)

model = vosk.Model('model_small')
record = vosk.KaldiRecognizer(model, 16000)
pa = pyaudio.PyAudio()
stream = pa.open(format=pyaudio.paInt16,
                 channels=1,
                 rate=16000,
                 input=True,
                 frames_per_buffer=8000)
stream.start_stream()


def listen():
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if record.AcceptWaveform(data) and len(data) > 0:
            answer = json.loads(record.Result())
            if answer['text']:
                yield answer['text']


def speak(say):
    tts.say(say)
    tts.runAndWait()


speak('starting')
print('start...')
for text in listen():
    if text == 'закрыть':
        quit()
    elif text == 'блокнот':
        os.system('notepad.exe')
    else:
        print(text)
