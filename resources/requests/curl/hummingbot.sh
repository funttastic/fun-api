HOST=https://localhost
PORT=5000

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
CERTIFICATES_FOLDER=$(readlink -f "$SCRIPT_DIR/../../.."/resources/certificates)

curl -X GET \
  --cert $CERTIFICATES_FOLDER/client_cert.pem \
  --key $CERTIFICATES_FOLDER/client_key.pem \
  --cacert $CERTIFICATES_FOLDER/ca_cert.pem \
  --header "Content-Type: application/json" \
  $HOST:$PORT/
