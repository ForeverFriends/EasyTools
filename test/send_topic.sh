#!/bin/ksh

TOPIC=""
MSG=""
TIME=1

usage() {
    local prog="`basename $1`"
    echo "Usage: -t topic -m message [p period]"
    echo "       $prog -h for help."
    echo "  -t   topic"
    echo "  -m   message"
    echo "  -p   period, default 1s"
    exit 1
}

while getopts "t:m:p:h" arg
do
        case $arg in
        t)  TOPIC=$OPTARG ;;
        m)  MSG=$OPTARG ;;
        p)  TIME=$OPTARG ;;
        h)  usage $0 ;;
        *)  usage $0 ;;
        esac
done


while true
do
    mega_ipc_tool -p ${TOPIC} -m ${MSG}
    sleep ${TIME}
done
