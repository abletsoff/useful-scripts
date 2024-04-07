#!/bin/bash

f_service_start () {
    iptables -t nat -N REDSOCKS
    iptables -t nat -A OUTPUT -d 10.2.0.0/16 -j REDSOCKS
    iptables -t nat -A OUTPUT -d 10.3.0.0/16 -j REDSOCKS
    iptables -t nat -A REDSOCKS -p tcp -j REDIRECT --to-ports 12345
}

f_service_stop () {
    iptables -t nat -D OUTPUT -d 10.2.0.0/16 -j REDSOCKS
    iptables -t nat -D OUTPUT -d 10.3.0.0/16 -j REDSOCKS
    iptables -t nat -D REDSOCKS -p tcp -j REDIRECT --to-ports 12345
    iptables -t nat -F REDSOCKS
    iptables -t nat -X REDSOCKS
}

argument=$1

if [[ $argument == "start" ]]; then
    f_service_start
elif [[ $argument == 'stop' ]]; then
    f_service_stop
fi
