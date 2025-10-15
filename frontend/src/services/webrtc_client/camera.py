# This file provides classes for capturing video from a local camera using OpenCV
# and integrating it as a video source for an `aiortc` WebRTC connection.
# The `_CameraCapture` class runs in a background thread to continuously grab frames,
# while `CameraVideoTrack` adapts this into a `VideoStreamTrack` consumable by `aiortc`.

import threading, cv2, numpy as np, asyncio
from typing import Optional
from aiortc.mediastreams import VideoStreamTrack
from av import VideoFrame


class _CameraCapture(threading.Thread):
    def __init__(
        self, device_index: int = 0, width: int = 640, height: int = 480, fps: int = 20
    ):
        super().__init__(daemon=True)
        self.cap = None
        self.device_index = device_index
        self.width = width
        self.height = height
        self.fps = fps
        self._running = True
        self.latest_bgr: Optional[np.ndarray] = None
        self.camera_error = False
        self._enabled = True
        self._init_camera()

    def _init_camera(self):
        """Initialize camera with error handling"""
        try:
            self.cap = cv2.VideoCapture(self.device_index)
            if not self.cap or not self.cap.isOpened():
                raise Exception("Cannot open camera")

            if self.width:
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            if self.height:
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            if self.fps:
                self.cap.set(cv2.CAP_PROP_FPS, self.fps)

            self.camera_error = False
        except Exception:
            self.camera_error = True
            self.cap = None

    def set_enabled(self, enabled: bool):
        """Enable or disable camera capture"""
        self._enabled = enabled
        if not enabled:
            # Create black frame when disabled
            self.latest_bgr = np.zeros(
                (self.height or 480, self.width or 640, 3), dtype=np.uint8
            )

    def run(self):
        while self._running:
            if not self._enabled or self.camera_error or not self.cap:
                # Show black frame or camera error frame
                if self.camera_error:
                    # Create error frame with text
                    error_frame = np.full(
                        (self.height or 480, self.width or 640, 3), 50, dtype=np.uint8
                    )
                    cv2.putText(
                        error_frame,
                        "Camera Error",
                        (200, 240),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (255, 255, 255),
                        2,
                    )
                    self.latest_bgr = error_frame
                elif not self._enabled:
                    # Black frame when camera is disabled
                    self.latest_bgr = np.zeros(
                        (self.height or 480, self.width or 640, 3), dtype=np.uint8
                    )
                cv2.waitKey(30)
                continue

            ret, frame = self.cap.read()
            if ret:
                self.latest_bgr = frame
            else:
                # Camera disconnected or error
                self.camera_error = True
            cv2.waitKey(30)

    def stop(self):
        self._running = False
        try:
            if self.cap:
                self.cap.release()
        except Exception:
            pass


class CameraVideoTrack(VideoStreamTrack):
    kind = "video"

    def __init__(self, capture: _CameraCapture, fps: int = 20):
        super().__init__()
        self.capture = capture
        self.fps = fps

    async def recv(self) -> VideoFrame:
        # pacing
        await asyncio.sleep(1 / float(self.fps))
        # get current frame
        frame = self.capture.latest_bgr
        if frame is None:
            # create black frame if not ready
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # BGR -> RGB
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        video_frame = VideoFrame.from_ndarray(rgb, format="rgb24")
        video_frame.pts, video_frame.time_base = await self.next_timestamp()
        return video_frame
