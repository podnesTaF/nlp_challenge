import whisper
import sounddevice as sd
import numpy as np
import soundfile as sf


class RealTimeSTT:
    def __init__(self, model_name="base", silence_threshold=0.27, silence_duration=3):
        """
        Initialize RealTimeSTT with Whisper model and silence detection parameters.
        """
        self.model = whisper.load_model(model_name)  # Load Whisper model
        self.sample_rate = 16000  # Required sample rate for Whisper
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.chunk_size = int(self.sample_rate * 0.1)  # Process chunks of 0.1 seconds
        self.audio_buffer = []  # Audio buffer to store recorded chunks
        self.running = True  # Control flag for stopping the recording

    def list_devices(self):
        """List all available audio devices."""
        print(sd.query_devices())

    def record_audio_with_silence_detection(self, device_index=None, debug_audio_filename="debug_audio.wav"):
        """Record audio until silence is detected and save debug audio."""
        print("Recording audio with silence detection...")

        self.audio_buffer = []  # Clear the buffer before recording
        silence_counter = 0  # Counter for silent chunks

        def callback(indata, frames, time, status):
            """Callback function to process incoming audio in real time."""
            nonlocal silence_counter

            if status:
                print(f"Status: {status}")
            audio_chunk = indata[:, 0]  # Get the first channel of audio

            # Normalize the audio chunk to handle low amplitude signals
            if np.max(np.abs(audio_chunk)) > 0:
                audio_chunk = audio_chunk / np.max(np.abs(audio_chunk))

            self.audio_buffer.append(audio_chunk)

            # Calculate the chunk's amplitude
            chunk_amplitude = np.abs(audio_chunk).mean()
            print(f"Chunk Amplitude: {chunk_amplitude:.5f}")

            # Check for silence
            if chunk_amplitude < self.silence_threshold:
                silence_counter += 1
            else:
                silence_counter = 0

            # Stop recording if silence persists
            if silence_counter > self.silence_duration / 0.1:  # Silence duration in chunks
                print("Silence detected, stopping recording.")
                self.running = False
                raise sd.CallbackStop()

        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.float32,
                blocksize=self.chunk_size,
                callback=callback,
                device=0,  # Allow device selection
            ):
                while self.running:
                    sd.sleep(100)  # Allow stream to process audio
        except sd.CallbackStop:
            print("Recording stopped gracefully.")
        except Exception as e:
            print(f"Error during recording: {e}")

        # Combine the audio buffer into a single array
        audio_data = np.concatenate(self.audio_buffer) if self.audio_buffer else np.array([])
        print(f"Recording complete. Captured {len(audio_data)} samples.")

        # Save debug audio
        self.save_debug_audio(audio_data, debug_audio_filename)
        return audio_data

    def save_debug_audio(self, audio_data, filename="debug_audio.wav"):
        """Save the recorded audio to a file for debugging."""
        if len(audio_data) == 0:
            print("No audio data to save.")
            return
        try:
            sf.write(filename, audio_data, self.sample_rate)
            print(f"Saved debug audio to '{filename}'.")
        except Exception as e:
            print(f"Error saving debug audio: {e}")

    def transcribe_audio(self, audio_data):
        """Transcribe audio using Whisper."""
        print("Transcribing audio...")
        try:
            result = self.model.transcribe(audio_data, fp16=False)
            return result["text"]
        except Exception as e:
            print(f"Error during transcription: {e}")
            return ""

    def listen_and_transcribe(self, device_index=None, debug_audio_filename="debug_audio.wav"):
        """Record and transcribe audio until silence is detected, saving debug audio."""
        self.running = True  # Reset the running flag before starting
        audio_data = self.record_audio_with_silence_detection(device_index, debug_audio_filename)
        if len(audio_data) == 0:
            print("No audio recorded for transcription.")
            return ""
        return self.transcribe_audio(audio_data)
