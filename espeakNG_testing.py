import pyttsx3

def speak(text):
    engine = pyttsx3.init()

    engine.setProperty('rate', 150)    # Speed percent (can go over 100)
    engine.setProperty('volume', 0.9)  # Volume 0-1

    # engine.say(text)
    print(text)

    engine.runAndWait()

if __name__ == "__main__":
    text_to_speak = "Hello! This is Your AI Home Assistant"
    speak(text_to_speak)