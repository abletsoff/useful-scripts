#!/usr/bin/env bash

wget -O urlhaus.txt https://urlhaus.abuse.ch/downloads/text_online/
declare -A seen
declare -A seen_full

while read -r url; do
    [[ -z ${url// } ]] && continue
    proto=${url%%://*}
    hostport=${url#*://}
    hostport=${hostport%%/*}
    if [[ $hostport != *:* ]]; then
        [[ $proto == https* ]] && hostport+=":443" || hostport+=":80"
    fi
    seen["$hostport"]=1
    [[ $proto == http ]] && seen_full["$url"]=1
done < urlhaus.txt

{
    for k in "${!seen_full[@]}"; do
        printf '"%s":\n' "$k"
    done
    for k in "${!seen[@]}"; do
        printf '"%s":\n' "$k"
    done
} | sort -u

rm urlhaus.txt
