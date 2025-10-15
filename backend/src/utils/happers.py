import socket
import json

decoder = json.JSONDecoder()


def ParseStream(buffer):
    while buffer:
        try:
            obj, idx = decoder.raw_decode(buffer)
            yield obj
            buffer = buffer[idx:].lstrip()
        except json.JSONDecodeError:
            break
    return buffer


def get_lan_ip():
    "Get the LAN IP address of the machine"
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # No need to actually connect, just get the IP of the default route
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip
