#!/bin/bash

user_agent="Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"
false_positive="Microsoft|PDF|Acrobat \d|Adobe |PowerPoint|^\d*$"

f_google_extractor () {
	url_allowed="[A-z,0-9,\/,\-,_,\.,~,&,=,\?,:]"
	html=$(curl -k -A "${user_agent}" \
		"https://www.google.com/search?q=site%3A${domain}+filetype%3A${filetype}"`
		`"${keyword_operator}&num=100" 2>/dev/null) 
	echo $var
	urls=$(echo $html | grep -o -P \
		"https?:\/\/[a-z,0-9,\.,\-]*${domain}${url_allowed}*\.(${filetype}|${filetype^^})")
	array=($urls)
	
	for url in "${array[@]}"; do
        echo $url
		if [[  $download_num -eq 0 ]]; then
			break
		fi
		download_num=$((download_num-1))	
	 	wget --no-check-certificate $url 2>&1 | grep -P "https?:\/\/${url_allowed}" 
	done
}

f_meta_retriving () {
	echo -e "\nExtracted metadata: "
	exiftool -creator -author * 2>/dev/null | sed "s/^.*: //g" | \
	   		grep -v -P "^===|^ |^$|${false_positive}" | sort -u	
}

f_print_help () {
	echo -e "Usage: meta-extractor.sh [options...]\n" \
                   "-h\t display this help and exit\n" \
		   "-d\t target domain\n" \
                   "-f\t filetype for metadata extraction [pdf,doc,ppt], default - pdf\n" \
		   "-p\t path to download in / extract from\n" \
		   "-l\t extract from local directory instead of downloading\n" \
		   "-n\t maximum allowed number of files to download, default - 100\n" \
		   "-k\t keyword for more specific results"
}

local_analyzing=0
filetype="pdf"
path="/tmp/meta-extraxtor_$(date '+%s')"
download_num=100

while getopts "hd:f:p:ln:k:" opt; do
    case $opt in
	   	h)	f_print_help
            exit ;;
		d)	domain=$OPTARG;;	
        f)	filetype=$OPTARG;;
		p)	path=$OPTARG;;
		l)	local_analyzing=1;;
		n)	download_num=$OPTARG;;
		k)  keyword_operator="+intext:$OPTARG";;
    esac
done

if [ ! -d "$path" ]; then
	mkdir $path
fi
cd $path
echo "Info: working directory is $path"

if [[ $local_analyzing -eq 0 ]]; then
	if [ -z "$domain" ]; then
		echo "Error: domain name should be specified"
		exit
	fi
	f_google_extractor
fi

f_meta_retriving
