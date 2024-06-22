#!/bin/bash

not_interactive="false"
main_url="https://icetrade.by/search/aucArchive?search_text=&zakup_type%5B1%5D=1&zakup_type%5B2%5D=1&auc_num=&okrb=&participant=&establishment=0&industries=&period=&created_from=&created_to=&request_end_from=&request_end_to=&t%5BTrade%5D=1&t%5BeTrade%5D=1&t%5BsocialOrder%5D=1&t%5BsingleSource%5D=1&t%5BAuction%5D=1&t%5BRequest%5D=1&t%5BcontractingTrades%5D=1&t%5Bnegotiations%5D=1&t%5BOther%5D=1&r%5B1%5D=1&r%5B2%5D=2&r%5B7%5D=7&r%5B3%5D=3&r%5B4%5D=4&r%5B6%5D=6&r%5B5%5D=5&sort=date%3Adesc&sbm=1&onPage=100&p="

# Change this
f_print_help () {
    echo -e "Usage: icetrade_scrapping.sh <pages> <domain>\n" \
        "-h\t\tdisplay this help and exit\n"
}

f_output () {
    match="false"
    for extracted_email in ${extracted_emails[@]}; do
        for email in ${emails[@]}; do
            if [[ $extracted_email == $email ]]; then
                match="true"
                break
            fi
        done
        if [[ $match == "false" ]]; then
            if [[ $not_interactive != "true" ]]; then

                if [[ $last_printed_status == "true" ]]; then
                    echo -en "\e[1A\e[K\e[1A"
                fi
                last_printed_status="false"
            fi
            shift 2
            echo $extracted_email
        fi
    done
}

while getopts "h" opt; do
    case $opt in
        h)  f_print_help
            exit;;
    esac
done
shift $((OPTIND-1))

pages_number=$1
company_title=$2

f_status () {
    message=$1
    
    # [1A - move  cursor up to 1 line
    # [K - Erase to end of line
    if [[ $not_interactive != "true" ]]; then
        if [[ $last_printed_status == "true" ]]; then
            echo -e "\e[1A\e[K\e[1A\nStatus: ${message}"
        else
            echo -e "\nStatus: ${message}"
        fi

        last_printed_status="true"
    fi
}

for i in $(seq 1 $pages_number); do
    url="${main_url}${i}"
    html_page=$(curl -s -k -G $url --data-urlencode "company_title=$company_title")
    extracted_tenders=$(echo $html_page | grep -o -P "https://icetrade.by/tenders/all/view/\d+")
    tenders=(${tenders[@]} ${extracted_tenders[@]})
done

total_url_amount=${#tenders[@]}
current_url=0

for tender_url in ${tenders[@]}; do
    current_url=$(($current_url+1))
    f_status "Process ${current_url}/${total_url_amount} URLs"

    tender_html=$(curl -k -s $tender_url)
    extracted_emails=$(echo "$tender_html" | grep -P -o "[\w\-\.]+@([\w\-]+\.)+[\w\-]+" | sort -u)
    f_output
    emails=(${emails[@]} ${extracted_emails[@]})
    
done
