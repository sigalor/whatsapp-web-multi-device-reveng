#!/usr/bin/env python3

import websocket
import traceback

from dissononce.processing.impl.handshakestate import HandshakeState
from dissononce.extras.processing.handshakestate_guarded import GuardedHandshakeState
from dissononce.extras.processing.handshakestate_switchable import SwitchableHandshakeState
from dissononce.processing.impl.cipherstate import CipherState
from dissononce.cipher.aesgcm import AESGCMCipher
from dissononce.hash.sha256 import SHA256Hash
from dissononce.dh.private import PrivateKey
from dissononce.extras.dh.dangerous.dh_nogen import NoGenDH
from dissononce.dh.x25519.x25519 import X25519DH
from dissononce.processing.handshakepatterns.interactive.XX import XXHandshakePattern

from consonance.dissononce_extras.processing.symmetricstate_wa import WASymmetricState
from consonance.certman.certman import CertMan


from .utilities import *
from .WAMessage_pb2 import *

prologue = b"WA\x05\x02"

ws = None
ephemeral_keypair = None
static_keypair = X25519DH().generate_keypair()
handshakestate = None


def on_message(ws, message):
  global handshakestate

  try:
    if not isinstance(message, bytes):
      print("expected bytes message")
      return

    msg_length = int.from_bytes(message[:3], "big")
    if len(message) < msg_length+3:
      print("invalid message length: " + str(msg_length))
      return
    msg = message[3:3+msg_length]
    print("message length: " + str(msg_length))

    server_handshake_resp = HandshakeMessage()
    server_handshake_resp.ParseFromString(msg)
    server_ephemeral = server_handshake_resp.serverHello.ephemeral
    server_static_ciphertext = server_handshake_resp.serverHello.static
    certificate_ciphertext = server_handshake_resp.serverHello.payload

    # literally everything copied from https://github.com/tgalal/consonance/blob/master/consonance/handshake.py#L102
    payload_buffer = bytearray()
    handshakestate.read_message(
        server_ephemeral + server_static_ciphertext + certificate_ciphertext, payload_buffer)

    certman = CertMan()
    if not certman.is_valid(handshakestate.rs, bytes(payload_buffer)):
      raise RuntimeError("certificate is invalid")

    #message_buffer = bytearray()

  except:
    eprint(traceback.format_exc())


def on_open(ws):
  global ephemeral_keypair, handshakestate

  try:
    ephemeral_public = bytearray()
    handshakestate.write_message(b"", ephemeral_public)

    msg = HandshakeMessage(clientHello=ClientHello(
        ephemeral=bytes(ephemeral_public))).SerializeToString()
    ws.send((prologue + len(msg).to_bytes(3, "big") +
            msg).ljust(64, b'\0'), websocket.ABNF.OPCODE_BINARY)
  except:
    eprint(traceback.format_exc())


def on_close(ws):
  print("close")


def initialize_multi_device(qr_keypair):
  global ws, ephemeral_keypair, static_keypair, handshakestate, prologue
  ephemeral_keypair = qr_keypair

  # copied from https://github.com/tgalal/consonance/blob/master/consonance/handshake.py#L61
  handshakestate = SwitchableHandshakeState(
      GuardedHandshakeState(
          HandshakeState(
              WASymmetricState(
                  CipherState(
                      AESGCMCipher()
                  ),
                  SHA256Hash()
              ),
              NoGenDH(X25519DH(), PrivateKey(ephemeral_keypair.private.data))
          )
      )
  )

  handshakestate.initialize(
      handshake_pattern=XXHandshakePattern(),
      initiator=True,
      prologue=prologue,
      s=static_keypair)

  # TODO: check if the Origin header is really needed
  ws = websocket.WebSocketApp("wss://web.whatsapp.com/ws/chat", on_message=on_message,
                              on_open=on_open, on_close=on_close, header={"Origin: https://web.whatsapp.com"})
  ws.run_forever()
