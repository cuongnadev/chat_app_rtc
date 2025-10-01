import asyncio, threading, cv2, pyaudio, numpy as np
from typing import Optional
from PySide6.QtCore import QObject, Signal
from aiortc import (
    RTCPeerConnection,
    RTCSessionDescription,
    RTCConfiguration,
    RTCIceServer,
)
from av import VideoFrame, AudioFrame

from .camera import _CameraCapture, CameraVideoTrack
from .microphone import _MicrophoneCapture, MicrophoneAudioTrack


class WebRTCClient(QObject):
    """WebRTC manager bound to a ChatClient for signaling.

    Usage:
    - Initiator: call start_call(target_username)
    - Receiver: call accept_offer(caller_username, sdp)
    """

    localFrame = Signal(object)  # numpy ndarray (RGB)
    remoteFrame = Signal(object)  # numpy ndarray (RGB)
    callEnded = Signal()
    error = Signal(str)
    cameraStateChanged = Signal(bool)  # camera enabled/disabled
    microphoneStateChanged = Signal(bool)  # microphone enabled/disabled

    def __init__(self, chat_client, stun_servers=None):
        super().__init__()
        self.chat_client = chat_client
        self.pc: Optional[RTCPeerConnection] = None
        self._loop = asyncio.new_event_loop()
        self._loop_thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._loop_thread.start()
        self._camera: Optional[_CameraCapture] = None
        self._camera_track: Optional[CameraVideoTrack] = None
        self._microphone: Optional[_MicrophoneCapture] = None
        self._audio_track: Optional[MicrophoneAudioTrack] = None
        self._partner: Optional[str] = None
        self._camera_enabled = True
        self._microphone_enabled = True
        self._track_tasks: set[asyncio.Task] = set()

        self._rtc_config = RTCConfiguration(
            iceServers=(
                stun_servers
                or [
                    RTCIceServer(urls="stun:stun.l.google.com:19302"),
                    RTCIceServer(urls="stun:stun1.l.google.com:19302"),
                ]
            )
        )

        # hook signaling from ChatClient
        self.chat_client.rtcAnswerReceived.connect(self._on_rtc_answer)
        self.chat_client.rtcEndReceived.connect(self._on_rtc_end)

        # emit local preview from capture thread via timer-ish approach
        self._preview_timer = threading.Thread(
            target=self._emit_preview_loop, daemon=True
        )
        self._preview_timer_running = False

    # ========== Public API ==========
    def start_call(self, partner_username: str):
        """Initiate a call to partner."""
        self._partner = partner_username
        asyncio.run_coroutine_threadsafe(self._start_call_async(), self._loop)

    def accept_offer(self, partner_username: str, sdp: str):
        """Accept an incoming offer from partner and send answer."""
        self._partner = partner_username
        asyncio.run_coroutine_threadsafe(self._accept_offer_async(sdp), self._loop)

    def set_remote_answer(self, sdp: str):
        asyncio.run_coroutine_threadsafe(self._set_remote_answer_async(sdp), self._loop)

    def end_call(self):
        asyncio.run_coroutine_threadsafe(self._end_call_async(), self._loop)
        # also notify partner
        if self._partner:
            try:
                self.chat_client.send_rtc_end(self._partner)
            except Exception:
                pass

    def toggle_camera(self):
        """Toggle camera on/off"""
        self._camera_enabled = not self._camera_enabled
        if self._camera:
            self._camera.set_enabled(self._camera_enabled)
        self.cameraStateChanged.emit(self._camera_enabled)

    def toggle_microphone(self):
        """Toggle microphone on/off"""
        self._microphone_enabled = not self._microphone_enabled
        if self._microphone:
            self._microphone.set_enabled(self._microphone_enabled)
        self.microphoneStateChanged.emit(self._microphone_enabled)

    @property
    def camera_enabled(self) -> bool:
        return self._camera_enabled

    @property
    def microphone_enabled(self) -> bool:
        return self._microphone_enabled

    # ========== Internal ==========
    def _ensure_pc(self):
        if self.pc is None:
            self.pc = RTCPeerConnection(self._rtc_config)

            @self.pc.on("track")
            async def on_track(track):
                print(f"📥 New track received: {track.kind}")
                print(f"📡 Received track: {track.kind}")
                # Run consumers concurrently to avoid blocking other tracks
                if track.kind == "video":
                    task = asyncio.create_task(self._consume_remote_video_track(track))
                elif track.kind == "audio":
                    task = asyncio.create_task(self._consume_remote_audio_track(track))
                else:
                    task = None

                if task is not None:
                    self._track_tasks.add(task)

                    def _done_cb(t: asyncio.Task):
                        try:
                            _ = t.result()
                        except Exception as e:
                            print(f"⚠️ Track consumer task ended with error: {e}")
                        finally:
                            self._track_tasks.discard(t)

                    task.add_done_callback(_done_cb)

            @self.pc.on("connectionstatechange")
            async def on_state_change():
                if self.pc and self.pc.connectionState in (
                    "failed",
                    "closed",
                    "disconnected",
                ):
                    await self._end_call_async()

    async def _prepare_local_media(self):
        # Prepare camera
        # Camera
        if self._camera is None:
            self._camera = _CameraCapture()
            self._camera.set_enabled(self._camera_enabled)
            self._camera.start()
            self._preview_timer_running = True
            # restart preview thread if stopped
            self._preview_timer = threading.Thread(
                target=self._emit_preview_loop, daemon=True
            )
            self._preview_timer.start()

        if self._camera_track is None:
            self._camera_track = CameraVideoTrack(self._camera)
            if self.pc:
                sender = self.pc.addTrack(self._camera_track)
                print(f"📹 Added video track: {self._camera_track.kind}")

        # Microphone
        if self._microphone is None:
            self._microphone = _MicrophoneCapture()
            self._microphone.set_enabled(self._microphone_enabled)

        if self._audio_track is None:
            self._audio_track = MicrophoneAudioTrack(self._microphone)
            if self.pc:
                sender = self.pc.addTrack(self._audio_track)
                print(f"🎤 Added audio track: {self._audio_track.kind}")

    def _emit_preview_loop(self):
        # Periodically emit latest frame for local preview
        while self._preview_timer_running:
            try:
                frame = self._camera.latest_bgr if self._camera else None
                if frame is not None:
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    # Check if signal still exists before emitting
                    if hasattr(self, "localFrame") and self.localFrame:
                        try:
                            self.localFrame.emit(rgb)
                        except RuntimeError as e:
                            if "Signal source has been deleted" in str(e):
                                print(
                                    "🎥 Preview signal deleted, stopping preview loop"
                                )
                                self._preview_timer_running = False
                                break
                            else:
                                raise  # Re-raise other RuntimeErrors
                cv2.waitKey(30)
            except Exception as e:
                if not self._preview_timer_running:  # Expected during shutdown
                    break
                print(f"⚠️ Preview loop error: {e}")
                cv2.waitKey(100)  # Wait longer on error

    async def _start_call_async(self):
        self._ensure_pc()
        await self._prepare_local_media()
        assert self.pc

        # Log tracks being added
        tracks = self.pc.getSenders()
        print(f"📡 Local tracks: {len(tracks)} tracks")
        for i, sender in enumerate(tracks):
            if sender.track:
                print(f"  Track {i}: {sender.track.kind}")

        offer = await self.pc.createOffer()
        await self.pc.setLocalDescription(offer)

        # Log SDP for debugging
        print("📋 Local SDP Offer:")
        sdp_lines = offer.sdp.split("\n")
        audio_lines = [line for line in sdp_lines if "audio" in line or "m=" in line]
        for line in audio_lines[:5]:  # Show first 5 relevant lines
            print(f"  {line}")

        # wait for ICE gathering to complete
        await self._wait_ice_gathering_complete(self.pc)
        # send offer
        self.chat_client.send_rtc_offer(self._partner, self.pc.localDescription.sdp)

    async def _accept_offer_async(self, sdp: str):
        self._ensure_pc()
        await self._prepare_local_media()
        assert self.pc

        # Log tracks being added
        tracks = self.pc.getSenders()
        print(f"📡 Local tracks: {len(tracks)} tracks")
        for i, sender in enumerate(tracks):
            if sender.track:
                print(f"  Track {i}: {sender.track.kind}")

        offer = RTCSessionDescription(sdp=sdp, type="offer")
        await self.pc.setRemoteDescription(offer)
        answer = await self.pc.createAnswer()
        await self.pc.setLocalDescription(answer)

        # Log answer SDP
        print("📋 Local SDP Answer:")
        sdp_lines = answer.sdp.split("\n")
        audio_lines = [line for line in sdp_lines if "audio" in line or "m=" in line]
        for line in audio_lines[:5]:  # Show first 5 relevant lines
            print(f"  {line}")

        await self._wait_ice_gathering_complete(self.pc)
        # send answer
        if self._partner:
            self.chat_client.send_rtc_answer(
                self._partner, self.pc.localDescription.sdp
            )

    async def _set_remote_answer_async(self, sdp: str):
        if not self.pc:
            # answer without existing pc: ignore
            return
        answer = RTCSessionDescription(sdp=sdp, type="answer")
        await self.pc.setRemoteDescription(answer)

    async def _consume_remote_video_track(self, track):
        try:
            while True:
                frame: VideoFrame = await track.recv()
                img = frame.to_ndarray(format="rgb24")
                self.remoteFrame.emit(img)
        except Exception:
            # track ended
            pass

    async def _consume_remote_audio_track(self, track):

        print("🔊 Starting remote audio track consumption...")
        p = pyaudio.PyAudio()

        # --- Tìm thiết bị output mặc định ---
        output_device_index = None
        channels = 1
        rate = 48000
        try:
            default_info = p.get_default_output_device_info()
            output_device_index = default_info["index"]
            channels = default_info["maxOutputChannels"]
            rate = int(default_info["defaultSampleRate"])
            print(f"🎧 Using default output device: {default_info['name']} ({channels}ch, {rate}Hz)")
        except IOError:
            print("❌ Cannot get default output device, using fallback")
            output_device_index = None

        # Mở stream PyAudio đúng channels và rate
        stream = p.open(
            format=pyaudio.paInt16,
            channels=channels,
            rate=rate,
            output=True,
            output_device_index=output_device_index,
            frames_per_buffer=960,  # tương ứng với chunk WebRTC 20ms
        )
        print("✅ Audio playback stream initialized")

        try:
            while True:
                frame: AudioFrame = await track.recv()
                audio_data = frame.to_ndarray(format="s16")

                # Nếu stereo, convert theo channels thiết bị
                if audio_data.ndim == 2:
                    if audio_data.shape[1] != channels:
                        # Reshape/copy kênh
                        if channels == 1:
                            audio_data = np.mean(audio_data, axis=1).astype(np.int16)
                        elif channels == 2:
                            if audio_data.shape[1] == 1:
                                audio_data = np.repeat(audio_data, 2, axis=1)
                            else:
                                audio_data = audio_data[:, :2]  # lấy 2 kênh đầu
                        else:
                            audio_data = audio_data[:, :channels]
                    audio_data = audio_data.flatten()
                else:
                    # mono
                    if channels > 1:
                        audio_data = np.repeat(audio_data, channels)

                stream.write(audio_data.tobytes())

        except Exception as e:
            print(f"⚠️ Track consumer stopped: {e}")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
            print("🔇 Remote audio playback stopped.")

    async def _end_call_async(self):
        # Close PC
        if self.pc:
            try:
                await self.pc.close()
            except Exception:
                pass
            self.pc = None

        # Cancel tasks
        for t in list(self._track_tasks):
            t.cancel()
        self._track_tasks.clear()

        # Stop camera
        if self._camera:
            self._preview_timer_running = False
            self._camera.stop()
            self._camera = None
        self._camera_track = None

        # Stop microphone
        if self._microphone:
            self._microphone.stop()
            self._microphone = None
        self._audio_track = None

        self._partner = None
        self.callEnded.emit()

    async def _wait_ice_gathering_complete(
        self, pc: RTCPeerConnection, timeout: float = 5.0
    ):
        if pc.iceGatheringState == "complete":
            return
        done = asyncio.Event()

        @pc.on("icegatheringstatechange")
        async def on_state_change():
            if pc.iceGatheringState == "complete":
                done.set()

        try:
            await asyncio.wait_for(done.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            pass

    # ========== ChatClient signaling handlers ==========
    def _on_rtc_answer(self, from_user: str, sdp: str):
        # only accept answer from current partner
        if self._partner and from_user == self._partner:
            self.set_remote_answer(sdp)

    def _on_rtc_end(self, from_user: str):
        if self._partner and from_user == self._partner:
            self.end_call()
