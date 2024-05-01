import os

from pathlib import Path

import requests
import ssl
import websocket

username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")
client_cert = Path("../certificates/client_cert.pem").absolute().resolve().as_posix()
client_key = Path("../certificates/client_key.pem").absolute().resolve().as_posix()

ssl_defaults = ssl.get_default_verify_paths()
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

target_id = "all.all"


def sign_in(username, password):
	url = "https://localhost:30001/auth/signIn"

	credentials = {"username": username, "password": password}

	response = requests.post(
		url,
		json=credentials,
		verify=False,  # In a production environment, you should verify SSL certificates
		cert=(client_cert, client_key)
	)

	if response.status_code == 200:
		return response.json()["token"]
	else:
		raise Exception("Authentication failed")


def on_message(_ws, message):
	print(f"on_message -> message: {message}")


def on_error(_ws, error):
	print(f"on_error -> error: {error}")


def on_close(ws, close_status_code, close_msg):
	print(f"on_close -> status: {close_status_code}, message: {close_msg}")


def on_open(ws):
	print(f'''on_open -> sending: "{target_id}"''')
	ws.send(target_id)
	print(f'''on_open -> sent: "{target_id}"''')


if __name__ == "__main__":
	token = sign_in(username, password)

	url = "wss://localhost:30001/ws/log"
	websocket.enableTrace(True)

	header = [
		f"Authorization: Bearer {token}",
	]

	ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
	ssl_context.load_cert_chain(certfile=client_cert, keyfile=client_key)
	ssl_context.check_hostname = False
	ssl_context.verify_mode = ssl.CERT_NONE

	ws = websocket.WebSocketApp(
		url,
		header=header,
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
