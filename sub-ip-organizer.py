#!/usr/bin/python3

import os
import sys
import re

ipv4_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
domains = sys.argv[1:]
dictionary = {}

for path, folders, files in os.walk(os.getcwd()):
    for filename in files:
        with open(os.path.join(os.getcwd(), filename)) as f:
            for line in f.readlines():
                for domain in domains:
                    domain_regex= r'[a-z,0-9,\.,\-]*' + domain
                    domain_matches = re.findall(domain_regex,line)
                    for domain_match in domain_matches:
                        ip_matches = re.findall(ipv4_pattern, line)
                        for ip in ip_matches:
                            if ip not in dictionary.keys():
                                dictionary[ip] = [domain_match]
                            else:
                                if domain_match not in dictionary[ip]:
                                    dictionary[ip].append(domain_match)

for key, value in sorted(dictionary.items()):
    print(key)
    for domain in value:
        print(f'\t{domain}')
