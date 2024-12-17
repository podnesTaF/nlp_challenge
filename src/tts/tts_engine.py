import pygame
import tempfile
import os
from gtts import gTTS
import threading


class TTSEngine:
    def __init__(self):
        """Initialize the TTS Engine."""
        pygame.mixer.init()  # Initialize the mixer module
        self.is_playing = False
        self.lock = threading.Lock()  # Lock for thread safety during playback

    def speak(self, text):
        """Speak the given text using gTTS and pygame."""
        if not isinstance(text, str):
          try:
              text = str(text)
          except Exception as e:
              print(f"Error converting input to string: {e}")
              return  # Skip invalid input

        if not text.strip():
            return  # Skip empty text

        # Stop any ongoing playback
        self.stop()

        # Create a temporary file for the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            tts = gTTS(text=text, lang="en")
            tts.save(temp_audio.name)
            temp_audio_path = temp_audio.name

        def play_audio():
            """Internal function to play the audio file."""
            try:
                with self.lock:  # Ensure thread safety
                    self.is_playing = True
                    pygame.mixer.music.load(temp_audio_path)
                    pygame.mixer.music.play()

                # Wait for the playback to complete
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)  # Avoid blocking the main thread
            finally:
                with self.lock:
                    self.is_playing = False
                if os.path.exists(temp_audio_path):
                    os.unlink(temp_audio_path)  # Clean up the temporary file

        # Run the playback in a separate thread
        threading.Thread(target=play_audio, daemon=True).start()

    def stop(self):
        """Stop the current audio playback."""
        with self.lock:
            if self.is_playing:
                pygame.mixer.music.stop()  # Stop playback immediately
                self.is_playing = False


# Example Usage
if __name__ == "__main__":
    tts = TTSEngine()

    tts.speak("This is the first message.")
    tts.speak("This is the second message, stopping the first.")
