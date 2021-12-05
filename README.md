# MQTT Chunks

Repository contains example code how to transfer files with MQTT persistent topic.

For publishing file to client id specific topic, you can use:
```bash
Usage: upload.py host port client_id file chunk_size
```

Example:
```bash
$ python3 upload.py broker.hivemq.com 1883 cid firmware 90000
connected to broker.hivemq.com 1883 with result code: 0
uploading file firmware chunk size = 90000 bytes
published to topic: cid/firmware/0
published to topic: cid/firmware/1
published to topic: cid/firmware/2
published to topic: cid/firmware/3
published to topic: cid/firmware/4
published to topic: cid/firmware/5
published to topic: cid/firmware
upload finished for: firmware with 6 chunks
```

For downloading file from client id specific topic, you can use:

```bash
Usage: download.py host port client_id file
```

Example:
```bash
connected to broker.hivemq.com 1883 with result code: 0
downloading file: firmware
subscribed to firmware topic: cid/firmware
read file chunk: cid/firmware/0
read file chunk: cid/firmware/1
read file chunk: cid/firmware/2
read file chunk: cid/firmware/3
read file chunk: cid/firmware/4
read file chunk: cid/firmware/5
download finished for file: firmware
```
