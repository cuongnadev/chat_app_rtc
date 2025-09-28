import numpy as np, asyncio, pyaudio
from aiortc.mediastreams import AudioStreamTrack
from av import AudioFrame

class _MicrophoneCapture:
    """Microphone audio capture using PyAudio"""

    def __init__(
        self, sample_rate: int = 48000, channels: int = 1, chunk_size: int = 960
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.audio = None
        self.stream = None
        self.enabled = True
        self.error = False
        self._init_audio()

    def _init_audio(self):
        """Initialize audio with error handling"""
        try:
            self.audio = pyaudio.PyAudio()
            print(
                f"🎤 Initializing microphone: {self.sample_rate}Hz, {self.channels}ch"
            )
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
            )
            self.error = False
            print("✅ Microphone initialized successfully")
        except Exception as e:
            print(f"❌ Microphone initialization failed: {e}")
            self.error = True
            self.stream = None
            self.audio = None

    def read(self):
        """Read audio data"""
        if not self.enabled or self.error or not self.stream:
            # Return silence
            return np.zeros(self.chunk_size, dtype=np.int16)

        try:
            data = self.stream.read(self.chunk_size, exception_on_overflow=False)
            audio_array = np.frombuffer(data, dtype=np.int16)

            # Debug: Log if we're capturing significant audio
            max_val = np.max(np.abs(audio_array))
            if max_val > 1000:  # Only log when there's significant audio
                print(f"🎤 Capturing audio: max level {max_val}")

            return audio_array
        except Exception as e:
            print(f"❌ Microphone read error: {e}")
            self.error = True
            return np.zeros(self.chunk_size, dtype=np.int16)

    def set_enabled(self, enabled: bool):
        """Enable or disable microphone"""
        self.enabled = enabled

    def stop(self):
        """Stop audio capture"""
        try:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            if self.audio:
                self.audio.terminate()
        except Exception:
            pass


class MicrophoneAudioTrack(AudioStreamTrack):
    kind = "audio"

    def __init__(self, mic_capture: _MicrophoneCapture):
        super().__init__()
        self.mic = mic_capture

    async def recv(self) -> AudioFrame:
        # Read audio data
        samples = self.mic.read()

        # Debug audio capture
        if not self.mic.error and self.mic.enabled and len(samples) > 0:
            max_val = np.max(np.abs(samples))
            if max_val > 1000:  # Only log significant audio to avoid spam
                print(f"🎤 Sending audio: {len(samples)} samples, max={max_val}")

        # Ensure correct shape for mono audio
        if len(samples.shape) == 1:
            samples = samples.reshape(1, -1)

        # Convert to AudioFrame with explicit format
        frame = AudioFrame.from_ndarray(samples, format="s16", layout="mono")
        frame.sample_rate = self.mic.sample_rate
        frame.pts, frame.time_base = await self.next_timestamp()
        return frame