#!/usr/bin/env python3
"""
    Usage: download.py host port client_id file
"""

import os
import sys
import time
import json
import threading
import _thread
import hashlib
import base64
import paho.mqtt.client as mqtt

summary = {}
chunks = []
file_array = b''
done = False

lock = threading.Lock()


def md5(data):
    return hashlib.md5(data).hexdigest()


def download(client, file):
    global done
    global chunks
    global file_array

    print("downloading file:", file)

    client_id = client._client_id.decode()
    topic = client_id + "/" + file

    # Subscribe to file info topic.
    client.subscribe(topic, qos=1)
    print("subscribed to firmware topic: " + topic)

    # Wait to retrieve all chunks.
    while True:
        time.sleep(1)
        if len(summary["chunks"]) == len(chunks):
            break

    # Check and decode all the chunks.
    for z in summary["chunks"]:
        for c in chunks:
            if topic + "/" + str(z["number"]) == c["topic"]:

                try:
                    fhash = md5(c["data"])

                    if z["hash"] == fhash:
                        data = base64.b64decode(c["data"])
                        file_array = b''.join([file_array, data])
                    else:
                        print("chunk corrupted:", c["topic"])

                except Exception as e:
                    print("error decoding chunk", e)
                    os._exit(1)
                    os.kill(os.getpid)

    # Check combined chunks hash and write it to file.
    if summary["file"]["hash"] == md5(file_array):
        try:
            f = open('./'+file+"_download", 'wb')
            f.write(file_array)
            f.close()
        except Exception as e:
            print("error writing file", e)
            os._exit(1)
            os.kill(os.getpid)

    print("download finished for file:", file)
    os._exit(0)
    os.kill(os.getpid)


def read_chunk(client, file, msg):
    global summary
    global chunks

    client_id = client._client_id.decode()

    # Get file summary chunk.
    try:
        if msg.topic == client_id + "/" + file:
            summary = json.loads(msg.payload)
            # print(json.dumps(summary, indent=4, sort_keys=True))

            for c in summary["chunks"]:
                client.subscribe(client_id+"/"+file+"/"+str(c["number"]), qos=1)

        else:
            lock.acquire()
            chunks.append({
                "topic": msg.topic,
                "data": msg.payload,
            })
            client.unsubscribe(msg.topic)
            print("read file chunk:", msg.topic)
            lock.release()

    except Exception as e:
        print("error reading chunk:", e)
        os._exit(0)
        os.kill(os.getpid)


def main(host="localhost", port=1883, client_id="client_id", file="test.txt"):
    if not os.path.isfile(file):
        print("error no file:", file)
        return 1

    def on_connect(c, u, f, rc):
        print("connected to", host, port, "with result code:", str(rc))

        t = threading.Thread(target=download, args=(c, file,))
        t.daemon = True
        t.start()

    def on_message(c, u, msg):
        _thread.start_new_thread(read_chunk, (c, file, msg,))

    client = mqtt.Client(client_id)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(host, port, 60)
    client.loop_forever()


if __name__ == "__main__":
    if len(sys.argv) == 5:
        main(
            host=sys.argv[1],
            port=int(sys.argv[2]),
            client_id=sys.argv[3],
            file=sys.argv[4],
        )
    else:
        print(__doc__)
