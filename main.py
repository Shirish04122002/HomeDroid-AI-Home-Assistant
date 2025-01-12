import os
import sys
import queue
import sounddevice as sd
import vosk
import subprocess
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

def process_llama_output(output):
    response = output.split('Assistant:')[-1].strip()
    return response

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

                    llama_cmd = [
                        './llama.cpp/llama-cli',
                        '-m', './~/models/Llama-2-7B-chat-hf-TQ2_0.gguf',  
                        '--prompt', f'User: {text}\nAssistant:',
                        '--n-predict', '50'
                    ]
                    
                    try:
                        llama_output = subprocess.check_output(llama_cmd, text=True)
                        response = process_llama_output(llama_output)
                        print(f"Assistant: {response}")

                        # subprocess.run(['espeak-ng', response])
                    except subprocess.CalledProcessError as e:
                        print(f"Error running LLaMA: {e}")
                    except Exception as e:
                        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()