# generate-qr

This PoC generates the QR code needed for logging in to WhatsApp Web. This is updated, compared to [the original version of this section in whatsapp-web-reveng](https://github.com/sigalor/whatsapp-web-reveng#logging-in). Note that the message format stays the same, see the description [here](https://github.com/sigalor/whatsapp-web-reveng#messages).

## 1. Connecting to the websocket

- simply open a WebSocket connection to `wss://web.whatsapp.com/ws`
- the HTTP header `Origin: https://web.whatsapp.com` must be set, otherwise the connection will be rejected

## 2. Asking for the QR code

1. Generate a client ID, consisting of 16 base64-encoded bytes.
2. Send a message to the websocket with the following five array entries:

- the string `admin`
- the string `init`
- the WhatsApp Web version, e.g. `[2,2126,11]`
- the operating system, browser and architecture, e.g. `["Linux","Chrome","x86_64"]`
- your client ID
- a boolean which is `true` if you're not in incognito mode and checked "Remember me"

# 3. Generating the QR code
