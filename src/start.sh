#!/bin/sh
modprobe v4l2_common

while true
do
    python3 /usr/local/src/app/http_server.py
    sleep 30
done
