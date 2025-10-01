import numpy as np
import asyncio
import pyaudio
import time
from aiortc.mediastreams import AudioStreamTrack
from av import AudioFrame


class _MicrophoneCapture:
    """Microphone audio capture using PyAudio"""

    def __init__(
        self, sample_rate: int = 48000, channels: int = 1, chunk_size: int = 960
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size  # Total elements (samples * channels)
        self.audio = None
        self.stream = None
        self.enabled = True
        self.error = False
        self._init_audio()

    def _adjust_chunk_size(self):
        """Adjust chunk_size to 20ms per frame (WebRTC standard), total elements"""
        samples_20ms = int(0.02 * self.sample_rate)
        self.chunk_size = samples_20ms * self.channels
        print(
            f"🔧 Adjusted chunk_size to {self.chunk_size} for {self.channels}ch @ {self.sample_rate}Hz"
        )

    def _init_audio(self):
        """Initialize audio with error handling and device priority"""
        try:
            self.audio = pyaudio.PyAudio()

            print("🔍 Searching for microphone devices...")
            selected_device = None
            preferred_devices = []  # List of 1-2ch devices first

            for i in range(self.audio.get_device_count()):
                info = self.audio.get_device_info_by_index(i)
                if info.get("maxInputChannels") > 0:
                    ch = int(info["maxInputChannels"])
                    rate = int(info["defaultSampleRate"])
                    print(f"  [{i}] {info['name']} - {ch}ch @ {rate}Hz")

                    # Prioritize: 1-2ch devices with rate close to target
                    if ch <= 2 and abs(rate - self.sample_rate) < 2000:
                        preferred_devices.append((i, info))
                    elif (
                        not selected_device and ch > 0
                    ):  # Fallback to any if no preferred
                        selected_device = info

            # Select first preferred if available
            if preferred_devices:
                _, selected_device = preferred_devices[0]

            if not selected_device:
                raise RuntimeError("❌ No input device found")

            device_index = selected_device["index"]
            self.channels = int(selected_device["maxInputChannels"])
            self.sample_rate = int(selected_device["defaultSampleRate"])
            self._adjust_chunk_size()

            frames_per_buffer = self.chunk_size // self.channels  # Samples per channel
            print(
                f"🎤 Using device {device_index}: {selected_device['name']} at {self.sample_rate}Hz, {self.channels}ch"
            )
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
            print(
                f"📊 Audio settings: {self.sample_rate}Hz, {self.channels}ch, {frames_per_buffer} frames/buffer"
            )
        except Exception as e:
            print(f"❌ Microphone initialization failed: {e}")
            self.error = True
            self.stream = None
            if self.audio:
                self.audio.terminate()
                self.audio = None

    def read(self):
        """Read audio data - returns format based on channels"""
        if not self.enabled or self.error or not self.stream:
            if self.error:
                print("♻️ Retrying microphone init...")
                time.sleep(1)
                self._init_audio()
            # Return silence in correct format
            samples_per_channel = self.chunk_size // self.channels
            if self.channels == 1:
                return np.zeros(samples_per_channel, dtype=np.int16)
            else:
                return np.zeros((samples_per_channel, self.channels), dtype=np.int16)

        try:
            frames_per_buffer = self.chunk_size // self.channels
            data = self.stream.read(frames_per_buffer, exception_on_overflow=False)
            audio_array = np.frombuffer(data, dtype=np.int16)

            # Reshape based on channels
            if self.channels == 1:
                # Mono: keep as 1D
                pass
            else:
                # Multi-channel: reshape to (samples, channels) - deinterleave
                samples_per_channel = len(audio_array) // self.channels
                audio_array = audio_array.reshape(samples_per_channel, self.channels)

            return audio_array
        except Exception as e:
            print(f"❌ Microphone read error: {e}")
            self.error = True
            samples_per_channel = self.chunk_size // self.channels
            if self.channels == 1:
                return np.zeros(samples_per_channel, dtype=np.int16)
            else:
                return np.zeros((samples_per_channel, self.channels), dtype=np.int16)

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

        if samples is None or len(samples) == 0 or samples.size == 0:
            samples_per_channel = self.mic.chunk_size // self.mic.channels
            if self.mic.channels == 1:
                samples = np.zeros(samples_per_channel, dtype=np.int16)
            else:
                samples = np.zeros(
                    (samples_per_channel, self.mic.channels), dtype=np.int16
                )

        try:
            # Convert to mono if multi-channel
            if self.mic.channels > 1:
                if samples.ndim == 2:
                    # samples shape is (frames, channels) - average across channels
                    samples = samples.mean(axis=1).astype(np.int16)
                elif samples.ndim == 1:
                    # Already flattened interleaved format, reshape first
                    samples_per_channel = len(samples) // self.mic.channels
                    samples = samples.reshape(samples_per_channel, self.mic.channels)
                    samples = samples.mean(axis=1).astype(np.int16)

            # Ensure 1D and contiguous for mono layout
            if samples.ndim > 1:
                samples = samples.flatten()
            samples = np.ascontiguousarray(samples)

            # Create frame with mono layout
            frame = AudioFrame.from_ndarray(samples, format="s16", layout="mono")
            frame.sample_rate = self.mic.sample_rate
        except Exception as e:
            print(
                f"⚠️ Audio frame build error: {e}, shape={samples.shape if samples is not None else None}, ndim={samples.ndim if samples is not None else None}"
            )
            # Create silence frame
            samples_per_channel = self.mic.chunk_size // self.mic.channels
            silence = np.zeros(samples_per_channel, dtype=np.int16)
            frame = AudioFrame.from_ndarray(silence, format="s16", layout="mono")
            frame.sample_rate = self.mic.sample_rate

        frame.pts, frame.time_base = await self.next_timestamp()
        return frame
