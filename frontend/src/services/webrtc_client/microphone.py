import numpy as np
import asyncio
import pyaudio
import time
import threading
from aiortc.mediastreams import AudioStreamTrack
from av import AudioFrame

# ---------------------------
# Microphone capture (PyAudio)
# ---------------------------
class _MicrophoneCapture:
    """Microphone audio capture using PyAudio"""

    def __init__(self, sample_rate: int = 48000, channels: int = 1, chunk_size: int = 960):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size  # total elements (samples * channels)
        self.audio = None
        self.stream = None
        self.enabled = True
        self.error = False
        self._init_audio()

    def _adjust_chunk_size(self):
        """Adjust chunk_size to 20ms per frame (WebRTC standard), total elements"""
        samples_20ms = int(0.02 * self.sample_rate)
        self.chunk_size = samples_20ms * self.channels
        print(f"🔧 Adjusted chunk_size to {self.chunk_size} for {self.channels}ch @ {self.sample_rate}Hz")

    def _init_audio(self):
        """Initialize audio with error handling and device priority"""
        try:
            self.audio = pyaudio.PyAudio()

            print("🔍 Searching for microphone devices...")
            selected_device = None  # will be tuple (index, info)
            preferred_devices = []  # list of (index, info) for 1-2ch devices first

            for i in range(self.audio.get_device_count()):
                info = self.audio.get_device_info_by_index(i)
                if info.get("maxInputChannels", 0) > 0:
                    ch = int(info["maxInputChannels"])
                    rate = int(info.get("defaultSampleRate", self.sample_rate))
                    name = info.get("name", f"device-{i}")
                    print(f"  [{i}] {name} - {ch}ch @ {rate}Hz")

                    # Prioritize: 1-2ch devices with rate close to target
                    if ch <= 2 and abs(rate - self.sample_rate) < 2000:
                        preferred_devices.append((i, info))
                    elif not selected_device and ch > 0:
                        selected_device = (i, info)

            # Select first preferred if available
            if preferred_devices:
                selected_device = preferred_devices[0]

            if not selected_device:
                raise RuntimeError("❌ No input device found")

            device_index, device_info = selected_device
            # set channels/rate based on device
            self.channels = int(device_info.get("maxInputChannels", self.channels))
            self.sample_rate = int(device_info.get("defaultSampleRate", self.sample_rate))
            self._adjust_chunk_size()

            frames_per_buffer = max(1, self.chunk_size // self.channels)  # samples per channel
            print(f"🎤 Using device {device_index}: {device_info.get('name')} at {self.sample_rate}Hz, {self.channels}ch")
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
            try:
                if self.stream:
                    self.stream.close()
            except Exception:
                pass
            self.stream = None
            if self.audio:
                try:
                    self.audio.terminate()
                except Exception:
                    pass
                self.audio = None

    def read(self) -> np.ndarray:
        """Read audio data as 1D interleaved int16 array (samples * channels)"""
        if not self.enabled or self.error or not self.stream:
            if self.error:
                print("♻️ Retrying microphone init...")
                time.sleep(1)
                self._init_audio()
            # Return silence 1D
            return np.zeros(self.chunk_size, dtype=np.int16)

        try:
            frames_per_buffer = max(1, self.chunk_size // self.channels)
            data = self.stream.read(frames_per_buffer, exception_on_overflow=False)
            audio_array = np.frombuffer(data, dtype=np.int16)

            # Ensure length is chunk_size; pad if necessary
            if audio_array.size != self.chunk_size:
                if audio_array.size < self.chunk_size:
                    pad = np.zeros(self.chunk_size - audio_array.size, dtype=np.int16)
                    audio_array = np.concatenate((audio_array, pad))
                else:
                    audio_array = audio_array[: self.chunk_size]

            # Debug: Log if capturing significant audio
            max_val = int(np.max(np.abs(audio_array))) if audio_array.size else 0
            if max_val > 1000:
                print(f"🎤 Capturing audio: level {max_val}, shape={audio_array.shape}")

            return audio_array  # 1D interleaved
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
                try:
                    self.stream.stop_stream()
                    self.stream.close()
                except Exception:
                    pass
            if self.audio:
                try:
                    self.audio.terminate()
                except Exception:
                    pass
        except Exception:
            pass


# ---------------------------
# AudioTrack for aiortc
# ---------------------------
class MicrophoneAudioTrack(MediaStreamTrack):
    kind = "audio"

    def __init__(self, mic_capture):
        super().__init__()
        self.mic = mic_capture

    async def recv(self) -> AudioFrame:
        samples = self.mic.read()

        # Nếu không có dữ liệu → silence
        if samples is None or samples.size == 0:
            samples = np.zeros(self.mic.chunk_size * self.mic.channels, dtype=np.int16)

        try:
            if self.mic.channels > 1:
                # reshape (frames, channels)
                frames = samples.size // self.mic.channels
                samples = samples[: frames * self.mic.channels]  # cắt phần dư nếu có
                samples = samples.reshape(frames, self.mic.channels)
                layout = "stereo" if self.mic.channels == 2 else f"{self.mic.channels}ch"
            else:
                samples = samples.flatten()
                layout = "mono"

            max_val = int(np.max(np.abs(samples)))
            if max_val > 500:
                print(f"📤 Sending frame: {samples.shape}, rate={self.mic.sample_rate}, "
                      f"ch={self.mic.channels}, layout={layout}, level={max_val}")

            frame = AudioFrame.from_ndarray(samples, format="s16", layout=layout)
        except Exception as e:
            print(f"⚠️ Audio frame build error: {e}, shape={samples.shape}")
            silence = np.zeros(self.mic.chunk_size, dtype=np.int16)
            layout = "mono"
            frame = AudioFrame.from_ndarray(silence, format="s16", layout=layout)

        frame.sample_rate = self.mic.sample_rate
        frame.pts, frame.time_base = await self.next_timestamp()
        return frame