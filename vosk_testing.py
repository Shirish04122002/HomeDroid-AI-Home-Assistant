import os
import sys
import queue
import sounddevice as sd
import vosk
import json

samplerate = 16000  
model_path = "vosk-model"

if not os.path.exists(model_path):
    print("Please download the Vosk model and unpack it as 'vosk-model' in the current folder.")
    sys.exit(1)

model = vosk.Model(model_path)
rec = vosk.KaldiRecognizer(model, samplerate)
q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(f"Status: {status}", file=sys.stderr)
    q.put(bytes(indata))


def main():
    print("Assistant is listening...")

    with sd.RawInputStream(
        samplerate=samplerate, blocksize=8000, dtype='int16',
        channels=1, callback=callback
    ):
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = rec.Result()
                text = json.loads(result).get("text", "")
                
                if text:
                    print(f"You said: {text}")


if __name__ == "__main__":
    main()

