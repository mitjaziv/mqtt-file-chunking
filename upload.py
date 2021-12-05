#!/usr/bin/env python3
"""
    Usage: upload.py host port client_id file chunk_size
"""

import os
import sys
import time
import json
import threading
import hashlib
import base64
import paho.mqtt.client as mqtt


def md5(file):
    hash_md5 = hashlib.md5()

    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()


def publish(client, topic, data):
    try:
        client.publish(topic, data, qos=1, retain=True)
        print("published to topic:", topic)
    except Exception as e:
        print("error publishing:", e)


def upload(client, file, chunk_size):
    print("uploading file", file, "chunk size =", chunk_size, "bytes")

    topic = client._client_id.decode() + "/" + file

    summary = {
        "time": str(int(time.time())),
        "file": {
            "name": file,
            "size": os.path.getsize(file),
            "hash": md5(file),
        },
        "chunks": []
    }

    i = 0
    with open(file, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if chunk:
                data = base64.b64encode(chunk)
                summary["chunks"].append({
                    "number": i,
                    "hash": hashlib.md5(data).hexdigest(),
                    "size_raw": len(chunk),
                    "size_b64": len(data)
                })
                publish(client, topic + "/" + str(i), data)
                i += 1
            else:
                break

    publish(client, topic, json.dumps(summary))

    # print(json.dumps(summary, indent=4, sort_keys=True))
    print("upload finished for:", file, "with", i, "chunks")

    time.sleep(1)
    os._exit(0)
    os.kill(os.getpid)


def main(host="localhost", port=1883, client_id="client_id", file="test.txt", chunk_size=90000):
    if not os.path.isfile(file):
        print("error no file:", file)
        return 1

    def on_connect(c, u, f, rc):
        print("connected to", host, port, "with result code:", str(rc))

        t = threading.Thread(target=upload, args=(c, file, chunk_size))
        t.daemon = True
        t.start()

    client = mqtt.Client(client_id)
    client.on_connect = on_connect

    client.connect(host, port, 60)
    client.loop_forever()


if __name__ == "__main__":
    if len(sys.argv) == 6:
        main(
            host=sys.argv[1],
            port=int(sys.argv[2]),
            client_id=sys.argv[3],
            file=sys.argv[4],
            chunk_size=int(sys.argv[5]),
        )
    else:
        print(__doc__)
