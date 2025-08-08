base_url="$DEFECTDOJO_API_URL"
auth_header="Authorization: Token $DEFECTDOJO_API_KEY"
base_url="$DEFECTDOJO_API_URL_EVB"
auth_header="Authorization: Token $DEFECTDOJO_API_KEY_EVB"

product_id='2'

f_get_engagements () {
    response=$(curl -s -k "$base_url/engagements/?limit=600&product=$product_id" \
        -H "$auth_header")
    engagements=$(echo "$response" | grep -o -P '"id":\d+' | cut -d ':' -f2)
}

f_del_engagements () {
    for engagement in $engagements; do
        if [[ "$engagement" == "4744" || "$engagement" == "5574" || "$engagement" == "5233" || "$engagement" == "5232" || "$engagement" == "4714" || "$engagement" == "4759" ]]; then
            continue
        fi
        echo $engagement
        time curl -X DELETE -k "$base_url/engagements/$engagement/" -H "$auth_header"
    done
    sleep 3
}

f_get_engagements
f_del_engagements
