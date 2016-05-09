#!/usr/bin/env bash

bin=$(dirname $0)
bin=$(cd "$bin"; pwd)

DEFAULT_WSP_HOME=$(cd "$bin"/../; pwd)
export WSP_HOME=${WSP_HOME:-$DEFAULT_WSP_HOME}

if [ $# -gt 1 ]; then
    if [ "$1" = "--config" ]; then
        shift
        conf_dir=$1
        if [ ! -d "$conf_dir" ]; then
            echo "Error: Cannot find directory of configuration files: $conf_dir"
        fi
        shift
        WSP_CONF_DIR=$conf_dir
    fi
fi

export WSP_CONF_DIR=${WSP_CONF_DIR:-"$WSP_HOME"/conf}

if [ -f "$WSP_CONF_DIR"/wsp-env.sh ]; then
    . "$WSP_CONF_DIR"/wsp-env.sh
fi

if [ "$WSP_LOG_DIR" = "" ]; then
    WSP_LOG_DIR=${WSP_LOG_DIR:-"$WSP_HOME"/log}
fi

if [ "$WSP_PID_DIR" = "" ]; then
    WSP_PID_DIR=${WSP_PID_DIR:-/tmp}
fi
