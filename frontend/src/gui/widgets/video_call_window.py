from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFrame,
    QGridLayout,
)
from PySide6.QtGui import QImage, QPixmap, QFont, QIcon
from PySide6.QtCore import Qt, QSize
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ASSETS_DIR = BASE_DIR / "assets"


class ControlButton(QPushButton):
    """Custom styled control button"""

    def __init__(
        self,
        text: str,
        icon_path: str = None,
        bg_color: str = "#4A5568",
        hover_color: str = "#2D3748",
    ):
        super().__init__(text)
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.setFixedSize(54, 54)

        if icon_path and Path(icon_path).exists():
            self.setIcon(QIcon(str(icon_path)))
            self.setIconSize(QSize(36, 36))

        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {bg_color};
                color: white;
                border: none;
                border-radius: 27px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {hover_color};
                transform: scale(0.95);
            }}
        """
        )


class VideoCallWindow(QDialog):
    def __init__(self, webrtc_client, partner_display: str):
        super().__init__()
        self.setWindowTitle(f"Video call with {partner_display}")
        self.resize(1100, 650)
        self.webrtc = webrtc_client
        self.partner_display = partner_display

        # Set window style
        self.setStyleSheet(
            """
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #1a202c, stop:1 #2d3748);
            }
        """
        )

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header with partner info
        self._create_header()
        main_layout.addWidget(self.header_widget)

        # Video container
        video_container = self._create_video_container()
        main_layout.addWidget(video_container, stretch=1)

        # Control panel
        controls_widget = self._create_controls()
        main_layout.addWidget(controls_widget)

        self.setLayout(main_layout)

    def _create_header(self):
        self.header_widget = QFrame()
        self.header_widget.setFixedHeight(80)
        self.header_widget.setStyleSheet(
            """
            QFrame {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
            }
        """
        )

        header_layout = QHBoxLayout(self.header_widget)
        header_layout.setContentsMargins(20, 0, 20, 0)

        # Partner info
        partner_label = QLabel(f"Video call with {self.partner_display}")
        partner_label.setStyleSheet(
            """
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                background: transparent;
            }
        """
        )

        # Call status
        self.status_label = QLabel("Connecting...")
        self.status_label.setStyleSheet(
            """
            QLabel {
                color: #68D391;
                font-size: 14px;
                background: transparent;
            }
        """
        )

        header_layout.addWidget(partner_label)
        header_layout.addStretch()
        header_layout.addWidget(self.status_label)

    def _create_video_container(self):
        container = QFrame()
        container.setStyleSheet(
            """
            QFrame {
                background-color: rgba(0, 0, 0, 0.3);
                border-radius: 20px;
            }
        """
        )

        container_layout = QGridLayout(container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(20)

        # Remote video (main view)
        self.remote_frame = QFrame()
        self.remote_frame.setStyleSheet(
            """
            QFrame {
                background-color: #000;
                border-radius: 15px;
                border: 2px solid #4A5568;
            }
        """
        )

        remote_layout = QVBoxLayout(self.remote_frame)
        remote_layout.setContentsMargins(0, 0, 0, 0)

        self.remote_label = QLabel("Waiting for remote video...")
        self.remote_label.setAlignment(Qt.AlignCenter)
        self.remote_label.setStyleSheet(
            """
            QLabel {
                color: #A0AEC0;
                font-size: 16px;
                background: transparent;
                border: none;
            }
        """
        )
        remote_layout.addWidget(self.remote_label)

        # Local video (small preview)
        self.local_frame = QFrame()
        self.local_frame.setFixedSize(280, 210)
        self.local_frame.setStyleSheet(
            """
            QFrame {
                background-color: #2D3748;
                border-radius: 15px;
                border: 2px solid #68D391;
            }
        """
        )

        local_layout = QVBoxLayout(self.local_frame)
        local_layout.setContentsMargins(0, 0, 0, 0)

        self.local_label = QLabel("Your video")
        self.local_label.setAlignment(Qt.AlignCenter)
        self.local_label.setStyleSheet(
            """
            QLabel {
                color: #E2E8F0;
                font-size: 14px;
                background: transparent;
                border: none;
            }
        """
        )
        local_layout.addWidget(self.local_label)

        # Layout arrangement
        container_layout.addWidget(self.remote_frame, 0, 0, 2, 2)
        container_layout.addWidget(
            self.local_frame, 0, 1, 1, 1, Qt.AlignTop | Qt.AlignRight
        )

        return container

    def _create_controls(self):
        controls_widget = QFrame()
        controls_widget.setFixedHeight(100)
        controls_widget.setStyleSheet(
            """
            QFrame {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 20px;
            }
        """
        )

        controls_layout = QHBoxLayout(controls_widget)
        controls_layout.setContentsMargins(30, 20, 30, 20)
        controls_layout.setSpacing(20)

        # Camera toggle button
        self.camera_btn = ControlButton("📷", bg_color="#68D391", hover_color="#48BB78")
        self.camera_btn.clicked.connect(self._toggle_camera)

        # Microphone toggle button
        self.mic_btn = ControlButton("🎤", bg_color="#4299E1", hover_color="#3182CE")
        self.mic_btn.clicked.connect(self._toggle_microphone)

        # Hang up button
        self.hangup_btn = ControlButton("📞", bg_color="#E53E3E", hover_color="#C53030")
        self.hangup_btn.clicked.connect(self._on_hangup)

        controls_layout.addStretch()
        controls_layout.addWidget(self.camera_btn)
        controls_layout.addWidget(self.mic_btn)
        controls_layout.addWidget(self.hangup_btn)
        controls_layout.addStretch()

        return controls_widget

    def _connect_signals(self):
        # Connect WebRTC signals
        self.webrtc.localFrame.connect(self._update_local)
        self.webrtc.remoteFrame.connect(self._update_remote)
        self.webrtc.callEnded.connect(self.accept)
        self.webrtc.cameraStateChanged.connect(self._on_camera_state_changed)
        self.webrtc.microphoneStateChanged.connect(self._on_microphone_state_changed)

        # Update status when connected
        self.status_label.setText("Connected")

    def _toggle_camera(self):
        self.webrtc.toggle_camera()

    def _toggle_microphone(self):
        self.webrtc.toggle_microphone()

    def _on_hangup(self):
        self.webrtc.end_call()

    def _on_camera_state_changed(self, enabled: bool):
        if enabled:
            self.camera_btn.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: #68D391;
                    color: white;
                    border: none;
                    border-radius: 27px;
                    font-size: 12px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #48BB78;
                }}
            """
            )
            self.camera_btn.setText("📷")
        else:
            self.camera_btn.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: #E53E3E;
                    color: white;
                    border: none;
                    border-radius: 27px;
                    font-size: 12px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #C53030;
                }}
            """
            )
            self.camera_btn.setText("📷❌")

    def _on_microphone_state_changed(self, enabled: bool):
        if enabled:
            self.mic_btn.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: #4299E1;
                    color: white;
                    border: none;
                    border-radius: 27px;
                    font-size: 12px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #3182CE;
                }}
            """
            )
            self.mic_btn.setText("🎤")
        else:
            self.mic_btn.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: #E53E3E;
                    color: white;
                    border: none;
                    border-radius: 27px;
                    font-size: 12px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #C53030;
                }}
            """
            )
            self.mic_btn.setText("🎤❌")

    def _ndarray_to_qpixmap(self, arr: np.ndarray) -> QPixmap:
        h, w, ch = arr.shape
        bytes_per_line = ch * w
        img = QImage(arr.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        return QPixmap.fromImage(img)

    def _update_local(self, frame: np.ndarray):
        pix = self._ndarray_to_qpixmap(frame)
        self.local_label.setPixmap(
            pix.scaled(
                self.local_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )
        self.local_label.setStyleSheet("""
        QLabel {
            background: transparent;
            border-radius: 15px; /* đồng bộ với frame */
        }
        """)
        # self.local_label.setScaledContents(True)

    def _update_remote(self, frame: np.ndarray):
        pix = self._ndarray_to_qpixmap(frame)
        self.remote_label.setPixmap(
            pix.scaled(
                self.remote_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )
