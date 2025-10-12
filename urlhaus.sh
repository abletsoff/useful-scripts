#!/usr/bin/env bash

wget -O urlhaus.txt https://urlhaus.abuse.ch/downloads/text_online/
set -euo pipefail
declare -A seen seen_full

# Define exclusions here
EXCLUDE=("gitlab.com:443" "docs.google.com:443" "drive.google.com:443")

while IFS= read -r url || [[ -n $url ]]; do
    url=${url//$'\r'/}           # remove CR
    [[ -z ${url// } ]] && continue
    [[ $url == http://* ]] && seen_full["$url"]=1
    host=${url#*://}; host=${host%%/*} || continue
    if [[ $host != *:* ]]; then
        [[ ${url,,} == https* ]] && host+=":443" || host+=":80"
    fi
    # Skip excluded hosts
    [[ " ${EXCLUDE[*]} " =~ " $host " ]] && continue
    seen["$host"]=1
done < urlhaus.txt

{ for k in "${!seen_full[@]}"; do printf '"%s":\n' "$k"; done
  for k in "${!seen[@]}"; do printf '"%s":\n' "$k"; done; } | sort -u
