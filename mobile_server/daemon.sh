#!/bin/bash

PORT_RANGE="8027 8035"
usage="Usage: $0 [start | stop]"

service="live_mobil_server"
SERVER_DIR="/data/androidesk/server/$service"
LOG_DIR="/tmp/androidesk/$service"
pid="$LOG_DIR/service.pid"
log="$LOG_DIR/service.log"

if [ ! -d $LOG_DIR ]; then
    mkdir -p "$LOG_DIR"
fi

case $1 in
    (start)

        for i in `seq $PORT_RANGE`
        do
            _pid=$pid.$i
            if [ -f $_pid ]; then
                if kill -0 `cat $_pid` > /dev/null 2>&1; then
                    echo $service running as process `cat $_pid`. Stop it first.
                    exit 1
                fi
            fi
            
            echo starting $service ...

            nohup ./main.py --port=$i >"$log.$i" 2>&1 < /dev/null &
            echo $! > "$_pid"
            sleep 0.3; head "$log.$i"
        done
        ;;


    (stop)

        for i in `seq $PORT_RANGE`
        do
            _pid=$pid.$i
            if [ -f $_pid ]; then
                if kill -0 `cat $_pid` > /dev/null 2>&1; then
                    echo stopping $service `cat $_pid` ...
                    kill `cat $_pid`
                else
                    echo no $service to stop
                fi
            else
                echo no $service to stop
            fi
        done
        ;;

    (test)
        ./main.py --port=8120
        ;;

    (*)
        echo $usage
        exit 1
        ;;


esac

