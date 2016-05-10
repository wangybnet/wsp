#!/usr/bin/env bash

if [ $# -le 1 ]; then
    exit 1
fi

bin=$(dirname $0)
bin=$(cd "$bin"; pwd)

. "$bin"/wsp-config.sh

oper=$1
shift
name=$1
shift

if [ ! -d "$WSP_LOG_DIR" ]; then
    mkdir -p "$WSP_LOG_DIR"
fi
if [ ! -d "$WSP_PID_DIR" ]; then
    mkdir -p "$WSP_PID_DIR"
fi

log="$WSP_LOG_DIR"/wsp-"$WSP_ID_STRING"-"$name".log
pid="$WSP_PID_DIR"/wsp-"$WSP_ID_STRING"-"$name".pid
stop_timeout=${WSP_STOP_TIMEOUT:-5}

case $oper in
    start)
        case $name in
            master)
                start_script="$WSP_HOME"/script/start-master.py
                ;;
            fetcher)
                start_script="$WSP_HOME"/script/start-fetcher.py
                ;;
            *)
                exit 1
                ;;
        esac
        nohup "$PYTHON" "$start_script" "$@" > "$log" 2>&1 < /dev/null &
        echo $! > "$pid"
        sleep 3
        if ! ps -p $! > /dev/null; then
            exit 1
        fi
        ;;
    stop)
        if [ -f "$pid" ]; then
            target_pid=$(cat "$pid")
            if kill -0 $target_pid > /dev/null 2>&1; then
                echo stopping $name
                kill $target_pid
                sleep $stop_timeout
                if kill -0 $target_pid > /dev/null 2>&1; then
                    echo "$name did not stop gracefully after $stop_timeout seconds: killing with kill -9"
                    kill -9 $target_pid
                fi
            else
                echo "no $name to stop"
            fi
            rm -f "$pid"
        else
            echo "no $name to stop"
        fi
        ;;
    *)
        exit 1
        ;;
esac
