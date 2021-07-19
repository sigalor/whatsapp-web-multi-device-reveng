#!/usr/bin/env python3

import websocket
import traceback

from .utilities import *
from .WAMessage_pb2 import *

intro_to_send = b"WA\x05\x02"

ws = None
keypair = None


def on_message(ws, message):
  if not isinstance(message, bytes):
    print("expected bytes message")
    return

  msg_length = int.from_bytes(message[:3], "big")
  if len(message) < msg_length+3:
    print("invalid message length: " + str(msg_length))
    return
  msg = message[3:3+msg_length]
  print("message length: " + str(msg_length))


def on_open(ws):
  global keypair

  try:
    msg = HandshakeMessage(clientHello=ClientHello(
        ephemeral=keypair.public.data)).SerializeToString()
    ws.send((intro_to_send + len(msg).to_bytes(3, "big") +
            msg).ljust(64, b'\0'), websocket.ABNF.OPCODE_BINARY)
  except:
    eprint(traceback.format_exc())

  pass


def on_close(ws):
  print("close")


def initialize_multi_device(qr_keypair):
  global ws, keypair
  keypair = qr_keypair

  # TODO: check if the Origin header is really needed
  ws = websocket.WebSocketApp("wss://web.whatsapp.com/ws/chat", on_message=on_message,
                              on_open=on_open, on_close=on_close, header={"Origin: https://web.whatsapp.com"})
  ws.run_forever()
