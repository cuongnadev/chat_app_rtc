import numpy as np
import time
import pyaudio
from aiortc.mediastreams import AudioStreamTrack
from av import AudioFrame


class _MicrophoneCapture:
    """Microphone audio capture using PyAudio"""

    def __init__(self, sample_rate: int = 48000, channels: int = 1, chunk_size: int = 960):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.audio = None
        self.stream = None
        self.enabled = True
        self.error = False
        self._init_audio()

    def _adjust_chunk_size(self):
        samples_20ms = int(0.02 * self.sample_rate)
        self.chunk_size = samples_20ms * self.channels
        print(f"🔧 Adjusted chunk_size to {self.chunk_size} for {self.channels}ch @ {self.sample_rate}Hz")

    def _init_audio(self):
        try:
            self.audio = pyaudio.PyAudio()
            print("🔍 Searching for microphone devices...")
            selected_device = None
            preferred_devices = []

            for i in range(self.audio.get_device_count()):
                info = self.audio.get_device_info_by_index(i)
                if info.get("maxInputChannels") > 0:
                    ch = int(info["maxInputChannels"])
                    rate = int(info["defaultSampleRate"])
                    print(f"  [{i}] {info['name']} - {ch}ch @ {rate}Hz")
                    if ch <= 2 and abs(rate - self.sample_rate) < 2000:
                        preferred_devices.append((i, info))
                    elif not selected_device and ch > 0:
                        selected_device = info

            if preferred_devices:
                _, selected_device = preferred_devices[0]

            if not selected_device:
                raise RuntimeError("❌ No input device found")

            device_index = selected_device["index"]
            self.channels = int(selected_device["maxInputChannels"])
            self.sample_rate = int(selected_device["defaultSampleRate"])
            self._adjust_chunk_size()

            frames_per_buffer = self.chunk_size // self.channels
            print(f"🎤 Using device {device_index}: {selected_device['name']} at {self.sample_rate}Hz, {self.channels}ch")
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=frames_per_buffer,
            )
            self.error = False
            print("✅ Microphone initialized successfully")
            print(f"📊 Audio settings: {self.sample_rate}Hz, {self.channels}ch, {frames_per_buffer} frames/buffer")
        except Exception as e:
            print(f"❌ Microphone initialization failed: {e}")
            self.error = True
            self.stream = None
            if self.audio:
                self.audio.terminate()
                self.audio = None

    def read(self):
        if not self.enabled or self.error or not self.stream:
            if self.error:
                print("♻️ Retrying microphone init...")
                time.sleep(1)
                self._init_audio()
            return np.zeros(self.chunk_size, dtype=np.int16)

        try:
            frames_per_buffer = self.chunk_size // self.channels
            data = self.stream.read(frames_per_buffer, exception_on_overflow=False)
            audio_array = np.frombuffer(data, dtype=np.int16)

            max_val = np.max(np.abs(audio_array))
            if max_val > 1000:
                print(f"🎤 Capturing audio: level {max_val}, shape={audio_array.shape}")

            return audio_array
        except Exception as e:
            print(f"❌ Microphone read error: {e}")
            self.error = True
            return np.zeros(self.chunk_size, dtype=np.int16)

    def set_enabled(self, enabled: bool):
        self.enabled = enabled

    def stop(self):
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

        if samples is None or len(samples) == 0 or samples.size == 0:
            samples = np.zeros(self.mic.chunk_size, dtype=np.int16)

        if self.mic.channels > 1:
            frames = samples.size // self.mic.channels
            samples = samples[: frames * self.mic.channels]
            samples = samples.reshape(frames, self.mic.channels)

            if self.mic.channels == 2:
                samples = samples.T  # (ch, samples)
                layout = "stereo"
            else:
                samples = samples.mean(axis=1).astype(np.int16)
                layout = "mono"
        else:
            samples = samples.flatten()
            layout = "mono"

        frame = AudioFrame.from_ndarray(samples, format="s16", layout=layout)
        frame.sample_rate = self.mic.sample_rate
        frame.pts, frame.time_base = await self.next_timestamp()
        return frame
