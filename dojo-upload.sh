#!/bin/bash

supported_tools=('Burp Scan' 'ZAP Scan' 'Nuclei Scan' 'Wpscan' 'Wpscan API Scan')
base_url="http://localhost:8080/api/v2"
auth_header="Authorization: Token $DEFECTDOJO_API_KEY_LOCAL"

f_print_help () {
    echo -e " DAST results upload to DefectDojo\n\n" \
    "Usage: dojo-upload.sh -f [File name] -t [Tool name] -p [Project name]\n\n" \
    "-h\t\tdisplay this help and exit\n" \
    "-f [File name] File name of DAST report\n" \
    "-t [Tool name] DAST tool name (e.g. BurpSuite, Zap)\n" \
    "-p [Product name] DefectDojo product name\n" \
    "-e [Engagement ID] DefectDojo engagement id" \
    "-l \t\tList of supported DAST tools"
}

f_print_tools () {
    for tool in "${supported_tools[@]}"; do
        echo " - $tool"
    done
}

f_handle_error () {
    message="$1"
    echo -e " Error: $message\n"
    f_print_help
}

f_get_product_id () {
    product_name_encode=$(echo "$product_name" | sed 's/ /%20/g')
    response=$(curl -s "$base_url/products/?name=$product_name_encode" \
        -H "$auth_header")
    product_id=$(echo "$response" | grep -o -P '"id":\d+' | cut -d ':' -f2)

    if [[ $(echo "$response" | grep -P '^{"count":1') == '' ]]; then
        f_handle_error "Product '$product_name' does not exist"
        exit 1
    fi
}

f_create_engagement () {
    engagement_name="$(echo "$tool_name" | sed 's/ /_/g')_$(date '+%Y-%m-%d')"
    response=$(curl -s -X POST "$base_url/engagements/" \
        -H "$auth_header" -H "Content-Type: application/json" \
        -d "{ 
          \"name\": \"${engagement_name}\",
          \"deduplication_on_engagement\": false,
          \"product\": $product_id,
          \"target_start\": \"$(date '+%Y-%m-%d')\",
          \"target_end\": \"$(date '+%Y-%m-%d')\"
      }")
      engagement_id=$(echo "$response" | grep -o -P '"id":\d+' | cut -d ':' -f2)
    
    if [[ $engagement_id == '' ]]; then
        f_handle_error "Unable to create engagement"
    fi      
}

f_upload_scan () {
    curl -s -X POST "$base_url/import-scan/" \
        -H "$auth_header" -H "Content-Type: multipart/form-data" \
        -F "scan_date=$(date '+%Y-%m-%d')" -F "engagement=$engagement_id" \
        -F "scan_type=$tool_name" \
        -F "deduplication_on_engagement=false" \
        -F "close_old_findings=true" \
        -F "close_old_findings_product_scope=true" \
        -F "file=@$filename"
    
}
f_tool_name () {
    for tool in "${supported_tools[@]}"; do
        if [[ $(echo "$tool" | grep -i "$tool_slang") != '' ]]; then
            tool_name="$tool"
        fi
    done

    if [[ "$tool_name" == '' ]]; then
        f_handle_error "'$tool_slang' is unsupported tool.\n"
    fi
}

while getopts "hf:t:p:e:l" opt; do
    case $opt in
        h) f_print_help
           exit;;
        f) filename="$OPTARG";;
        t) tool_slang="$OPTARG";;
        p) product_name="$OPTARG";;
        e) engagement_id="$OPTARG";;
        l) f_print_tools
           exit;;
    esac
done

if [[ $filename == '' || $tool_slang == '' || $product_name == '' ]]; then
    f_handle_error "Not all arguments"
fi

f_tool_name
f_get_product_id
if [[ $engagement_id == "" ]]; then
    f_create_engagement
fi
echo "Engagement: $engagement_id"

f_upload_scan
