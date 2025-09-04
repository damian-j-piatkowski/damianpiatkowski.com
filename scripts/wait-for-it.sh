#!/usr/bin/env bash
# Use this script to test if a given TCP host/port are available

TIMEOUT=15

usage() {
    echo "Usage: $0 host:port [-t timeout] [-- command args]"
    echo "  -h HOST | --host=HOST       Host or IP under test"
    echo "  -p PORT | --port=PORT       TCP port under test"
    echo "  -t TIMEOUT | --timeout=TIMEOUT Timeout in seconds, zero for no timeout"
    echo "  -q | --quiet                Don't output any status messages"
    echo "  -- COMMAND ARGS             Execute command with args after the test finishes"
    exit 1
}

wait_for() {
    if [[ "$TIMEOUT" -gt 0 ]]; then
        echo "Waiting $TIMEOUT seconds for $HOST:$PORT"
    else
        echo "Waiting for $HOST:$PORT without a timeout"
    fi
    start_ts=$(date +%s)
    while : ; do
        (echo > /dev/tcp/"$HOST"/"$PORT") >/dev/null 2>&1
        result=$?
        if [[ "$result" -eq 0 ]]; then
            end_ts=$(date +%s)
            echo "$HOST:$PORT is available after $((end_ts - start_ts)) seconds"
            break
        fi
        sleep 1
        current_ts=$(date +%s)
        elapsed_time=$((current_ts - start_ts))
        if [[ "$TIMEOUT" -gt 0 && "$elapsed_time" -ge "$TIMEOUT" ]]; then
            echo "Timeout occurred after waiting $TIMEOUT seconds for $HOST:$PORT"
            exit 1
        fi
    done
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        *:* )
        HOST=${1%%:*}
        PORT=${1##*:}
        shift
        ;;
        -h)
        HOST="$2"
        if [[ "$HOST" == "" ]]; then break; fi
        shift 2
        ;;
        --host=*)
        HOST="${1#*=}"
        shift
        ;;
        -p)
        PORT="$2"
        if [[ "$PORT" == "" ]]; then break; fi
        shift 2
        ;;
        --port=*)
        PORT="${1#*=}"
        shift
        ;;
        -t)
        TIMEOUT="$2"
        if [[ "$TIMEOUT" == "" ]]; then break; fi
        shift 2
        ;;
        --timeout=*)
        TIMEOUT="${1#*=}"
        shift
        ;;
        -q | --quiet)
        # This option is parsed but not used
        shift
        ;;
        --)
        shift
        break
        ;;
        --help)
        usage
        ;;
        *)
        echo "Unknown argument: $1"
        usage
        ;;
    esac
done

if [[ "$HOST" == "" || "$PORT" == "" ]]; then
    echo "Error: you need to provide a host and port to test."
    usage
fi

wait_for
exec "$@"
