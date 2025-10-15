# This file provides a utility function to parse a stream of data
# that may contain multiple concatenated JSON objects.

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