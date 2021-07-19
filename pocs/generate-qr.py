#!/usr/bin/env python3

import sys
import os
import websocket
import time
import base64
import json
import curve25519
import pyqrcode
import traceback

message_index = 0
ws = None
client_id = None
tags_map = {}  # stores the tags of all sent messages so that their responses can be matched

server_ref = None
private_key = None
public_key = None


def get_timestamp():
  return int(time.time())


def get_message_tag(name):
  global message_index
  tag = str(get_timestamp()) + ".--" + str(message_index)
  tags_map[tag] = name
  message_index += 1
  return tag


def eprint(*args, **kwargs):  # from https://stackoverflow.com/a/14981125
  print(*args, file=sys.stderr, **kwargs)


def generate_qr_code():
  pass


def on_message(ws, message):
  global server_ref, private_key, public_key, tags_map

  try:
    [tag, content] = message.split(",", 1)
    if tag not in tags_map:
      print(content)
      return

    tag_name = tags_map[tag]
    del tags_map[tag]

    if tag_name == "ask_for_qr":
      server_ref = json.loads(content)["ref"]
      private_key = curve25519.Private()
      public_key = private_key.get_public()
      qr_code_data = server_ref + "," + \
          str(base64.b64encode(public_key.serialize())) + "," + client_id
      pyqrcode.create(qr_code_data).png("qr.png", scale=6)
  except:
    eprint(traceback.format_exc())


def on_error(ws, error):
  pass


def on_open(ws):
  global client_id
  client_id = str(base64.b64encode(os.urandom(16)))
  payload = json.dumps(["admin", "init", [2, 2126, 11], [
      "Linux", "Chrome", "x86_64"], client_id, True], separators=(',', ':'))
  ws.send(get_message_tag("ask_for_qr") + "," + payload)


def on_close(ws):
  pass


ws = websocket.WebSocketApp("wss://web.whatsapp.com/ws", on_message=on_message, on_error=on_error,
                            on_open=on_open, on_close=on_close, header={"Origin: https://web.whatsapp.com"})
ws.run_forever()
