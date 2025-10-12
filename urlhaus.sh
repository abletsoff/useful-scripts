#!/usr/bin/env bash

wget -O urlhaus.txt https://urlhaus.abuse.ch/downloads/text_online/
set -euo pipefail
declare -A seen
declare -A seen_full

while read -r url; do
    [[ -z ${url// } ]] && continue

    # Preserve full http:// URLs
    [[ $url == http://* ]] && seen_full["$url"]=1

    # Extract host
    hostport=${url#*://}
    hostport=${hostport%%/*}
    [[ -z $hostport ]] && continue

    # Add default port if missing
    if [[ $hostport != *:* ]]; then
        [[ ${url,,} == https* ]] && hostport+=":443" || hostport+=":80"
    fi

    seen["$hostport"]=1
done < urlhaus.txt

## Output Wazuh list format
{
   for k in "${!seen_full[@]}"; do echo "$k"; done
   for k in "${!seen[@]}"; do echo "$k"; done
} | sort -u
