base_url="$DEFECTDOJO_API_URL"
auth_header="Authorization: Token $DEFECTDOJO_API_KEY"
base_url="$DEFECTDOJO_API_URL_EVB"
auth_header="Authorization: Token $DEFECTDOJO_API_KEY_EVB"

product_id='6'

f_get_engagements () {
    response=$(curl -s -k "$base_url/engagements/?limit=600&product=$product_id" \
        -H "$auth_header")
    engagements=$(echo "$response" | grep -o -P '"id":\d+' | cut -d ':' -f2)
}

f_del_engagements () {
    for engagement in $engagements; do
        if [[ "$engagement" == "5240" || "$engagement" == "5241" || "$engagement" == "5263" || "$engagement" == "5292" || "$engagement" == "5288" ]]; then
            continue
        fi
        echo $engagement
        time curl -X DELETE -k "$base_url/engagements/$engagement/" -H "$auth_header"
    done
    sleep 3
}

f_get_engagements
f_del_engagements
