import socket
import threading
import json
import sys

from utils import ParseStream

clients = {}  # username -> {"conn": socket, "display_name": str}
decoder = json.JSONDecoder()


def broadcast_user_list():
    """Gửi danh sách user tới tất cả client"""
    for username, info in list(clients.items()):
        users = [
            {"username": u, "display_name": c["display_name"]}
            for u, c in clients.items()
            if u != username   # loại bỏ chính mình
        ]
        payload = json.dumps({"type": "USERS", "users": users})
        try:
            info["conn"].send(payload.encode())
        except:
            pass


def send_to_client(target_username, payload):
    """Gửi payload JSON tới một client"""
    if target_username in clients:
        try:
            clients[target_username]["conn"].send(json.dumps(payload).encode())
        except:
            pass


def handle_client(conn, addr):
    username = None
    buffer = ""
    try:
        while True:
            raw = conn.recv(4096).decode()
            if not raw:
                break

            buffer += raw
            # parse nhiều JSON object trong buffer
            new_buffer = ""
            for msg in ParseStream(buffer):
                if msg.get("type") == "LOGIN":
                    username = msg["username"]
                    display_name = msg["display_name"]
                    clients[username] = {"conn": conn, "display_name": display_name}
                    print(f"{display_name} ({username}) joined")

                    # gửi xác nhận LOGIN_OK cho client
                    conn.send(json.dumps({"type": "LOGIN_OK"}).encode())

                    # broadcast cho người khác
                    broadcast_user_list()

                elif msg.get("type") == "MESSAGE":
                    target = msg.get("to")
                    text = msg.get("message")
                    if target in clients:
                        payload = {
                            "type": "MESSAGE",
                            "from": display_name,
                            "message": text
                        }
                        send_to_client(target, payload)
                    else:
                        conn.send(json.dumps({
                            "type": "ERROR",
                            "message": f"User {target} not online"
                        }).encode())

                elif msg.get("type") == "BROADCAST":
                    text = msg.get("message")
                    payload = {
                        "type": "BROADCAST",
                        "from": display_name,
                        "message": text
                    }
                    for u in list(clients.keys()):
                        if u != username:
                            send_to_client(u, payload)

                elif msg.get("type") == "GET_USERS":
                    users = [
                        {"username": u, "display_name": c["display_name"]}
                        for u, c in clients.items()
                        if u != username
                    ]
                    conn.send(json.dumps({"type": "USERS", "users": users}).encode())

            buffer = new_buffer

    except Exception as e:
        print("Error:", e)
    finally:
        if username and username in clients:
            print(f"{clients[username]['display_name']} ({username}) disconnected")
            del clients[username]
            broadcast_user_list()
        conn.close()


def app(host="127.0.0.1", port=4105):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen()
    server.settimeout(1.0)
    print(f"Server listening on {host}:{port}")

    try:
        while True:
            try:
                conn, addr = server.accept()
                thread = threading.Thread(
                    target=handle_client, args=(conn, addr), daemon=True
                )
                thread.start()
            except socket.timeout:
                continue
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        for u, info in list(clients.items()):
            info["conn"].close()
        server.close()
        sys.exit(0)
