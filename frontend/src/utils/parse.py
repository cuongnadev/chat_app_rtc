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

from PySide6.QtCore import QThread, Signal