#!/bin/bash

if [ -f "resources_temp/setup/docker/Dockerfile" ]; then
  cp -R resources_temp/* resources
  rm -rf resources_temp
  chmod -R ug+rwx resources
  python resources/scripts/generate_ssl_certificates.py --passphrase "$SELECTED_PASSPHRASE" --cert-path resources/certificates
  sed -i "s/<password>/$SELECTED_PASSPHRASE/g" resources/configuration/production.yml
  sed -i '/telegram:/,/enabled: true/ s/enabled: true/enabled: false/' resources/configuration/common.yml
  sed -i '/logging:/,/use_telegram: true/ s/use_telegram: true/use_telegram: false/' resources/configuration/production.yml
  python app.py
fi

exec python app.py
