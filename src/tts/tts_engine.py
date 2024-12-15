import pyttsx3

class TTSEngine:
    def __init__(self):
        """Initialize the text-to-speech engine."""
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Adjust the rate of speech
        self.engine.setProperty('volume', 0.9)  # Set the volume level

    def speak(self, text):
      try:
          self.engine.say(text)
          self.engine.runAndWait()
      except RuntimeError as e:
          print(f"Error during TTS: {e}")
