import ssl
import websocket

ssl_defaults = ssl.get_default_verify_paths()
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


def on_message(_ws, message):
	print(f"on_message -> message: {message}")


def on_error(_ws, error):
	print(f"on_error -> error: {error}")


def on_close(ws, close_status_code, close_msg):
	print(f"on_close -> status: {close_status_code}, message: {close_msg}")


def on_open(ws):
	print(f'''on_open -> sending: "all"''')

	ws.send("all")

	print(f'''on_open -> sent: "all"''')


if __name__ == "__main__":
	url = "wss://localhost:30001/ws/log"
	websocket.enableTrace(True)

	ws = websocket.WebSocketApp(
		url,
		on_message=on_message,
		on_error=on_error,
		on_close=on_close,
		on_open=on_open,
	)

	ws.run_forever(
		sslopt={
			"cert_reqs": ssl.CERT_NONE,
			"ssl_version": ssl.PROTOCOL_TLS,
			"context": ssl_context
		}
	)
