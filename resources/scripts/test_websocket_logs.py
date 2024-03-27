import ssl
import websocket

ssl_defaults = ssl.get_default_verify_paths()
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


def on_message(ws, message):
	print("Received '%s'" % message)


def on_error(ws, error):
	print("Error '%s'" % error)


def on_close(ws, close_status_code, close_msg):
	print("### closed ###")


def on_open(ws):
	print("Sending 'all'...")
	ws.send("all")
	print("Sent")


if __name__ == "__main__":
	websocket.enableTrace(True)
	ws = websocket.WebSocketApp(
		"wss://localhost:30001/ws/log",
		on_message=on_message,
		on_error=on_error,
		on_close=on_close,
		on_open=on_open,
	)

	ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE, "ssl_version": ssl.PROTOCOL_TLS, "context": ssl_context})
