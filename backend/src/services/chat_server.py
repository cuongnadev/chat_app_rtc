import socket
import threading
import json
import sys

from utils import ParseStream, get_lan_ip

clients = {}  # username -> {"conn": socket, "display_name": str}
groups = {}  # group_name -> {"members": [usernames]}
decoder = json.JSONDecoder()


def broadcast_user_list():
    """Send list of online users to all clients"""
    for username, info in list(clients.items()):
        users = [
            {"username": u, "display_name": c["display_name"]}
            for u, c in clients.items()
            if u != username
        ]
        group_list = [
            {"username": g, "display_name": f"#{g}", "type": "group"}
            for g in groups.keys()
            if username in groups[g]["members"]
        ]
        payload = json.dumps({"type": "USERS", "users": users + group_list})
        try:
            info["conn"].send(payload.encode())
        except:
            pass


def send_to_client(target_username, payload):
    print("server: ", payload)
    """Send JSON payload to a client"""
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
            # parse multiple JSON objects in buffer
            new_buffer = ""
            for msg in ParseStream(buffer):
                if msg.get("type") == "LOGIN":
                    username = msg["username"]
                    display_name = msg["display_name"]
                    clients[username] = {"conn": conn, "display_name": display_name}
                    print(f"{display_name} ({username}) joined")

                    # Send LOGIN_OK confirmation to client
                    conn.send(json.dumps({"type": "LOGIN_OK"}).encode())

                    # Broadcast to others
                    broadcast_user_list()

                elif msg.get("type") == "MESSAGE":
                    target = msg.get("to")
                    text = msg.get("message")
                    from_username = msg.get("from")
                    if target in clients:
                        payload = {
                            "type": "MESSAGE",
                            "from": display_name,
                            "message": text,
                            "from_username": from_username,
                        }
                        send_to_client(target, payload)
                    else:
                        conn.send(
                            json.dumps(
                                {
                                    "type": "ERROR",
                                    "message": f"User {target} not online",
                                }
                            ).encode()
                        )

                elif msg.get("type") == "FILE":
                    target = msg.get("to")
                    filename = msg.get("filename")
                    b64data = msg.get("data")
                    if target in clients and target != username:
                        payload = {
                            "type": "FILE",
                            "from": display_name,
                            "filename": filename,
                            "data": b64data,
                        }
                        send_to_client(target, payload)
                    else:
                        conn.send(
                            json.dumps(
                                {
                                    "type": "ERROR",
                                    "message": f"User {target} not online",
                                }
                            ).encode()
                        )

                elif msg.get("type") == "BROADCAST":
                    text = msg.get("message")
                    payload = {
                        "type": "BROADCAST",
                        "from": display_name,
                        "message": text,
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

                # ==== WebRTC signaling relay ====
                elif msg.get("type") == "RTC_OFFER":
                    target = msg.get("to")
                    if target in clients and target != username:
                        payload = {
                            "type": "RTC_OFFER",
                            "from": username,
                            "from_display": clients[username]["display_name"],
                            "sdp": msg.get("sdp"),
                        }
                        send_to_client(target, payload)
                    else:
                        conn.send(
                            json.dumps(
                                {
                                    "type": "ERROR",
                                    "message": f"User {target} not online",
                                }
                            ).encode()
                        )

                elif msg.get("type") == "RTC_ANSWER":
                    target = msg.get("to")
                    if target in clients and target != username:
                        payload = {
                            "type": "RTC_ANSWER",
                            "from": username,
                            "from_display": clients[username]["display_name"],
                            "sdp": msg.get("sdp"),
                        }
                        send_to_client(target, payload)
                    else:
                        conn.send(
                            json.dumps(
                                {
                                    "type": "ERROR",
                                    "message": f"User {target} not online",
                                }
                            ).encode()
                        )

                elif msg.get("type") == "RTC_ICE":
                    target = msg.get("to")
                    if target in clients and target != username:
                        payload = {
                            "type": "RTC_ICE",
                            "from": username,
                            "candidate": msg.get("candidate"),
                        }
                        send_to_client(target, payload)
                    else:
                        conn.send(
                            json.dumps(
                                {
                                    "type": "ERROR",
                                    "message": f"User {target} not online",
                                }
                            ).encode()
                        )

                elif msg.get("type") == "RTC_END":
                    target = msg.get("to")
                    if target in clients and target != username:
                        payload = {
                            "type": "RTC_END",
                            "from": username,
                        }
                        send_to_client(target, payload)
                    else:
                        conn.send(
                            json.dumps(
                                {
                                    "type": "ERROR",
                                    "message": f"User {target} not online",
                                }
                            ).encode()
                        )

                elif msg.get("type") == "JOIN_GROUP":
                    group_name = msg.get("group_name")
                    username = msg.get("username")

                    if group_name not in groups:
                        conn.send(json.dumps({
                            "type": "ERROR",
                            "message": f"Group '{group_name}' does not exist."
                        }).encode())
                    else:
                        members = groups[group_name]["members"]
                        if username not in members:
                            members.append(username)
                            print(f"{username} joined group {group_name}")
                            broadcast_user_list()  # cập nhật danh sách cho tất cả
                            conn.send(json.dumps({
                                "type": "SUCCESS",
                                "message": f"Joined group '{group_name}' successfully!"
                            }).encode())
                        else:
                            conn.send(json.dumps({
                                "type": "INFO",
                                "message": f"You are already in group '{group_name}'."
                            }).encode())

                elif msg.get("type") == "CREATE_GROUP":
                    group_name = msg.get("group_name")
                    members = msg.get("members", [])
                    if group_name not in groups:
                        groups[group_name] = {"members": members}
                        print(f"Group created: {group_name} -> {members}")
                        broadcast_user_list()
                    else:
                        conn.send(json.dumps({
                            "type": "ERROR",
                            "message": f"Group {group_name} already exists"
                        }).encode())

                elif msg.get("type") == "GROUP_MESSAGE":
                    group_name = msg.get("group_name")
                    text = msg.get("message")
                    from_username = msg.get("from")

                    if group_name in groups:
                        members = groups[group_name]["members"]
                        payload = {
                            "type": "GROUP_MESSAGE",
                            "from": from_username,
                            "group_name": group_name,
                            "message": text,
                        }
                        for member in members:
                            if member in clients and member != from_username:
                                send_to_client(member, payload)

            buffer = new_buffer

    except Exception as e:
        print("Error:", e)
    finally:
        if username and username in clients:
            print(f"{clients[username]['display_name']} ({username}) disconnected")
            del clients[username]
            broadcast_user_list()
        conn.close()


def app(port=4105):
    ip_lan = get_lan_ip()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.bind((ip_lan, port))

    server.listen()
    server.settimeout(1.0)
    print(f"Server listening on {ip_lan}:{port}")
    print(f"Clients in LAN use this IP to connect")

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
