import sys
import time
import base64


def get_timestamp():
  return int(time.time())


def eprint(*args, **kwargs):  # from https://stackoverflow.com/a/14981125
  print(*args, file=sys.stderr, **kwargs)


def to_base64(data):
  return base64.b64encode(data).decode("utf8")
