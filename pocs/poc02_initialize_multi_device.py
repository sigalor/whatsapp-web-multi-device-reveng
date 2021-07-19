#!/usr/bin/env python3

import websocket

ws = None


def on_message(ws, message):
  print(message)


def on_open(ws):
  pass


def on_close(ws):
  print("close")


def initialize_multi_device():
  global ws
  # TODO: check if the Origin header is really needed
  ws = websocket.WebSocketApp("wss://web.whatsapp.com/ws/chat", on_message=on_message,
                              on_open=on_open, on_close=on_close, header={"Origin: https://web.whatsapp.com"})
  ws.run_forever()
