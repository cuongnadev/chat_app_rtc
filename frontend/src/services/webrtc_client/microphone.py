import numpy as np, asyncio, pyaudio
from aiortc.mediastreams import AudioStreamTrack
from av import AudioFrame

class _MicrophoneCapture:
    """Microphone audio capture using PyAudio"""

    def __init__(
        self, sample_rate: int = 16000, channels: int = 1, chunk_size: int = 320
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.audio = None
        self.stream = None
        self.enabled = True
        self.error = False
        self._init_audio()

    def _adjust_chunk_size(self):
        """Adjust chunk_size to 20ms per frame (WebRTC standard)"""
        if self.sample_rate == 16000:
            self.chunk_size = 320   # 20ms @ 16kHz
        elif self.sample_rate == 48000:
            self.chunk_size = 960   # 20ms @ 48kHz
        else:
            print(f"⚠️ Unsupported rate {self.sample_rate}, using chunk_size={self.chunk_size}")

    def _init_audio(self):
        """Initialize audio with error handling"""
        try:
            self.audio = pyaudio.PyAudio()

            print("🔍 Searching for microphone devices...")
            selected_device = None

            for i in range(self.audio.get_device_count()):
                info = self.audio.get_device_info_by_index(i)
                if info.get("maxInputChannels") > 0:
                    print(f"  [{i}] {info['name']} - {info['maxInputChannels']}ch @ {int(info['defaultSampleRate'])}Hz")
                    # Ưu tiên device có rate gần với self.sample_rate
                    if abs(int(info['defaultSampleRate']) - self.sample_rate) < 2000:
                        selected_device = info
                        break


            # Nếu không tìm thấy thì lấy device đầu tiên có input
            if not selected_device:
                for i in range(self.audio.get_device_count()):
                    info = self.audio.get_device_info_by_index(i)
                    if info.get("maxInputChannels") > 0:
                        selected_device = info
                        break

            if not selected_device:
                raise RuntimeError("❌ No input device found")

            device_index = selected_device["index"]
            device_rate = int(selected_device["defaultSampleRate"])
            if device_rate != self.sample_rate:
                print(f"⚠️ Device supports {device_rate}Hz, overriding {self.sample_rate}Hz")
                self.sample_rate = device_rate

            self._adjust_chunk_size()

            print(f"🎤 Using device {device_index}: {selected_device['name']} at {self.sample_rate}Hz")
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
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
            if self.error:  # Nếu lỗi thì thử init lại
                print("♻️ Retrying microphone init...")
                self._init_audio()
            # Trả về silence đúng shape
            return np.zeros((self.channels, self.chunk_size), dtype=np.int16)

        try:
            data = self.stream.read(self.chunk_size, exception_on_overflow=False)
            audio_array = np.frombuffer(data, dtype=np.int16)

            if self.channels == 1:
                # Mono → reshape thành (samples, 1)
                audio_array = audio_array.reshape(-1, 1)
            elif self.channels > 1:
                # Stereo → (samples, channels)
                audio_array = audio_array.reshape(-1, self.channels)

            # Debug: Log if we're capturing significant audio
            max_val = np.max(np.abs(audio_array))
            if max_val > 1000:  # Only log when there's significant audio
                print(f"🎤 Capturing audio: level {max_val}, shape={audio_array.shape}")

            return audio_array
        except Exception as e:
            print(f"❌ Microphone read error: {e}")
            self.error = True
            return np.zeros((self.channels, self.chunk_size), dtype=np.int16)

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
        samples = self.mic.read()

        if samples is None or len(samples) == 0:
            silence = np.zeros((self.mic.chunk_size, self.mic.channels), dtype=np.int16)
            samples = silence

        layout = "mono" if self.mic.channels == 1 else "stereo"

        try:
            frame = AudioFrame.from_ndarray(samples, format="s16", layout=layout)
        except Exception as e:
            print(f"⚠️ Audio frame build error: {e}, shape={samples.shape}")
            silence = np.zeros((self.mic.chunk_size, self.mic.channels), dtype=np.int16)
            frame = AudioFrame.from_ndarray(silence, format="s16", layout=layout)

        frame.sample_rate = self.mic.sample_rate
        frame.pts, frame.time_base = await self.next_timestamp()
        return frame
