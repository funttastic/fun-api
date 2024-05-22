import requests
import ssl
from pathlib import Path

username = "root"
password = "asdf"
ca_cert = Path("../certificates/ca_cert.pem").absolute().resolve().as_posix()
client_cert = Path("../certificates/client_cert.pem").absolute().resolve().as_posix()
client_key = Path("../certificates/client_key.pem").absolute().resolve().as_posix()

ssl_defaults = ssl.get_default_verify_paths()
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

target_id = "fun-client.back"


def sign_in(username, password):
	url = "https://localhost:30001/auth/signIn"

	credentials = {"username": username, "password": password}

	response = requests.post(
		url,
		json=credentials,
		verify=ca_cert,  # In a production environment, you should verify SSL certificates
		cert=(client_cert, client_key)
	)

	if response.status_code == 200:
		return response.json()["token"]
	else:
		raise Exception("Authentication failed")


def	test_request(token):
	url = "https://localhost:30001/development/test"
	headers = {
		"Authorization": f"Bearer {token}"
	}
	response = requests.get(
		url,
		headers=headers,
		json={},
		verify=ca_cert,  # In a production environment, you should verify SSL certificates
		cert=(client_cert, client_key)
	)
	if response.status_code == 200:
		return response
	else:
		return None

if __name__ == "__main__":
	token = sign_in(username, password)
	response = test_request(token)
	if response:
		print(response)
	else:
		print("Request failed")
