#!/bin/bash

f_verify () {
        readarray -t emails < $emails_file
        for email in ${emails[@]}; do
                result=$(check_if_email_exists $email)
                is_reachable=$(echo "$result" | grep '"is_reachable"' | sed "s/,//g" | cut -d ":" -f 2)
                echo "$email - $is_reachable"
                sleep 1
        done
}

emails_file=$1
f_verify
