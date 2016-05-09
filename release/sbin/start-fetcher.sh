#!/usr/bin/env bash

bin=$(dirname $0)
bin=$(cd "$bin"; pwd)

. "$bin"/wsp-config.sh

echo "Starting fetcher"
"$WSP_HOME"/sbin/wsp-daemon.sh start fetcher
