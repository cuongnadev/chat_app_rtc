# Lấy thư mục gốc project
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"

chat_list = [
    {
        "avatar": str(ASSETS_DIR / "avatarC.png"),
        "name": "Cường Dev",
        "last_message": "Tin nhắn mới nhất",
        "last_active_time": "2 hours",
    },
    {
        "avatar": str(ASSETS_DIR / "avatarV.png"),
        "name": "Trần Vinh",
        "last_message": "Tin nhắn mới nhất",
        "last_active_time": "2 hours",
    },
    {
        "avatar": str(ASSETS_DIR / "avatarB.png"),
        "name": "Ka Bun",
        "last_message": "Đang xem...",
        "last_active_time": "5 minutes",
    },
    {
        "avatar": str(ASSETS_DIR / "avatarT.png"),
        "name": "Đông Thi",
        "last_message": "Ai làm bài tập chưa?",
        "last_active_time": "1 day",
    },
]
