#!/usr/bin/env python3

import os
import websocket
import json
import curve25519
import pyqrcode
import traceback
from dissononce.dh.x25519.x25519 import X25519DH

from .utilities import *
from .poc02_initialize_multi_device import initialize_multi_device

message_index = 0
ws = None
client_id = None

server_ref = None
keypair = None


message_index = 0
tags_map = {}  # stores the tags of all sent messages so that their responses can be matched


def get_message_tag(name):
  global message_index
  tag = str(get_timestamp()) + ".--" + str(message_index)
  tags_map[tag] = name
  message_index += 1
  return tag


def on_message(ws, message):
  global server_ref, keypair, tags_map

  try:
    if isinstance(message, bytes):
      print("received bytes, which is not supported by this code, use a phone where multi-device is enabled instead")
      ws.close()
      return

    [tag, content] = message.split(",", 1)
    content_parsed = json.loads(content)

    if tag in tags_map:
      tag_name = tags_map[tag]
      del tags_map[tag]

      if tag_name == "ask_for_qr":
        server_ref = content_parsed["ref"]
        keypair = X25519DH().generate_keypair()
        qr_code_data = server_ref + "," + \
            to_base64(keypair.public.data) + "," + client_id
        pyqrcode.create(qr_code_data, error="L").png("qr.png", scale=6)
        print("created QR code: " + qr_code_data)
    elif isinstance(content_parsed, list) and content_parsed[0] == "Cmd" and content_parsed[1]["type"] == "upgrade_md_prod":
      print("switching to multi-device communication protocol")
      initialize_multi_device(keypair)
  except:
    eprint(traceback.format_exc())


def on_open(ws):
  global client_id

  try:
    client_id = to_base64(os.urandom(16))
    payload = json.dumps(["admin", "init", [2, 2126, 11], [
        "Linux", "Chrome", "x86_64"], client_id, True], separators=(',', ':'))
    ws.send(get_message_tag("ask_for_qr") + "," + payload)
  except:
    eprint(traceback.format_exc())


def main():
  global ws
  ws = websocket.WebSocketApp("wss://web.whatsapp.com/ws", on_message=on_message,
                              on_open=on_open, header={"Origin: https://web.whatsapp.com"})
  ws.run_forever()


if __name__ == '__main__':
  main()
