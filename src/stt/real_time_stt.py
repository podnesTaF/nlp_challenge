import whisper
import sounddevice as sd
import numpy as np

class RealTimeSTT:
    def __init__(self, model_name="base"):
        self.model = whisper.load_model(model_name)  # Load Whisper model
        self.sample_rate = 16000  # Required sample rate for Whisper

    def record_audio(self, duration=5):
        """Record audio for a given duration."""
        print(f"Recording audio for {duration} seconds...")
        audio = sd.rec(int(duration * self.sample_rate), samplerate=self.sample_rate, channels=1, dtype=np.float32)
        sd.wait()  # Wait for the recording to complete
        print("Recording complete.")
        return audio.squeeze()

    def transcribe_audio(self, audio_data):
        """Transcribe audio using Whisper."""
        print("Transcribing audio...")
        result = self.model.transcribe(audio_data, fp16=False)
        return result["text"]

    def listen_and_transcribe(self, duration=5):
        """Record and transcribe audio for a fixed duration."""
        audio_data = self.record_audio(duration)
        return self.transcribe_audio(audio_data)
