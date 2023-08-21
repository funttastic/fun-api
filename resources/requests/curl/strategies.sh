#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

source "$SCRIPT_DIR/common.sh"

strategy_start() {
	local strategy=""
	local version=""
	local id=""

	while [[ $# -gt 0 ]]; do
		case "$1" in
			--strategy) strategy="$2"; shift ;;
			--version) version="$2"; shift ;;
			--id) id="$2"; shift ;;
			*) shift ;;
		esac
		shift
	done

	strategy=${strategy:-$STRATEGY}
	version=${version:-$VERSION}
	id=${id:-$ID}

	send_request \
	--method "POST" \
	--url "/strategy/start" \
	--payload "{
		\"strategy\": \"$strategy\",
		\"version\": \"$version\",
		\"id\": \"$id\"
	}"
}

strategy_stop() {
	local strategy=""
	local version=""
	local id=""

	while [[ $# -gt 0 ]]; do
		case "$1" in
			--strategy) strategy="$2"; shift ;;
			--version) version="$2"; shift ;;
			--id) id="$2"; shift ;;
			*) shift ;;
		esac
		shift
	done

	strategy=${strategy:-$STRATEGY}
	version=${version:-$VERSION}
	id=${id:-$ID}

	send_request \
	--method "POST" \
	--url "/strategy/stop" \
	--payload "{
		\"strategy\": \"$strategy\",
		\"version\": \"$version\",
		\"id\": \"$id\"
	}"
}
