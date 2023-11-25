# Usage:
#   docker run -dt --name=<template> -p <exposed port>:5000 -v /path/to/shared/folder:/media/shared <template>
#   curl -d '{}' -H "Content-Type: application/json" -X POST http://localhost:<exposed port>/

FROM ubuntu:latest

ARG DEBIAN_FRONTEND=noninteractive
ARG TZ="Etc/GMT"

ARG CLONE_BRANCH="development"

ENV PORT="${PORT:-5000}"

RUN set -ex \
  && apt-get update \
  && apt-get install --no-install-recommends -y \
    ca-certificates \
    openssh-server \
    git \
    python3 \
    python3-pip \
#  && apt clean \
#  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
  && ln -s /usr/bin/python3 /usr/bin/python \
#  && ln -s /usr/bin/pip3 /usr/bin/pip \
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
  && cd resources/configuration \
  && cp production.example.yml production.yml \ 
  && cd ../strategies \
  && cp -R templates/* . \
  && set +ex

WORKDIR /root/app

RUN set -ex \
  && mv resources resources_temp \
  && set +ex

# Needs to coincide with what's defined inside of the configuration file.
EXPOSE $PORT

# CMD python app.py
CMD cp -R resources_temp/* resources && rm -rf resources_temp && /bin/bash
