# Usage:
#   docker build --build-arg RANDOM_PASSPHRASE=<your_random_passphrase> -t <image_name> .
#   docker run -dt --name=<container_name> -p <exposed_port>:5000 -v /path/to/shared/folder:/media/shared <image_name>
#   curl -d '{}' -H "Content-Type: application/json" -X POST http://localhost:<exposed_port>/

FROM ubuntu:latest

ARG DEBIAN_FRONTEND=noninteractive
ARG TZ="Etc/GMT"

ARG CLONE_BRANCH="development"

# ARG GATEWAY_PASSPHRASE
ENV GATEWAY_PASSPHRASE=""

ARG RANDOM_PASSPHRASE
# ENV RANDOM_PASSPHRASE=""

ENV PORT="${PORT:-5000}"

RUN groupadd docker

RUN set -ex \
  && apt-get update \
  && apt-get install --no-install-recommends -y \
    ca-certificates \
    openssh-server \
    git \
    vim \
    python3 \
    python3-pip \
  && ln -s /usr/bin/python3 /usr/bin/python \
  && set +ex

RUN set -ex \
  && git clone -b $CLONE_BRANCH https://github.com/funttastic/fun-hb-client.git /tmp/app \
  && mkdir /root/app \
  && mv /tmp/app/* /root/app/ \
  && rm -rf /tmp/app \
  && cd /root/app \
  && pip install -r requirements.txt \
  && set +ex

WORKDIR /root/app

RUN set -ex \
  && mkdir -p resources/certificates \
  && cd resources/configuration \
  && cp production.example.yml production.yml \
  && cd ../strategies \
  && cp -R templates/* . \
  && set +ex

WORKDIR /root/app

# RUN if [ -z "$RANDOM_PASSPHRASE" ]; then echo "No random passphrase provided." > resources/random_passphrase.txt; else echo "A new random passphrase has been saved in the file 'resources/random_passphrase.txt'. Keep it in a safe place."; echo "$RANDOM_PASSPHRASE" > resources/random_passphrase.txt; GATEWAY_PASSPHRASE="$RANDOM_PASSPHRASE"; fi
RUN if [ ! -z "$RANDOM_PASSPHRASE" ]; then echo "A new random passphrase has been saved in the file 'resources/random_passphrase.txt'. Keep it in a safe place."; echo "$RANDOM_PASSPHRASE" > resources/random_passphrase.txt; GATEWAY_PASSPHRASE="$RANDOM_PASSPHRASE"; fi

RUN set -ex \
  && mv resources resources_temp \
  && set +ex

EXPOSE $PORT

CMD cp -R resources_temp/* resources \
&& rm -rf resources_temp \
&& chown -RH :docker resources \
&& chown -RH :docker resources/certificates \
&& chmod -R ug+rwx resources \
&& python resources/scripts/generate_ssl_certificates.py --passphrase $GATEWAY_PASSPHRASE --cert-path resources/certificates \
&& /bin/bash

