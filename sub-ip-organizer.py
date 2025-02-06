#!/usr/bin/python3

import os
import sys
import re
import argparse

ipv4_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
dictionary = {}

parser = argparse.ArgumentParser()
parser.add_argument('--domains', nargs='+', type=str, help="Domains")
parser.add_argument('--addresses', nargs='+', type=str, help="Addresses files")
args = parser.parse_args()
domains = args.domains
if not domains:
    domains = []

for path, folders, files in os.walk(os.getcwd()):
    for filename in files:
        with open(os.path.join(os.getcwd(), filename)) as f:
            for line in f.readlines():
                # Exclude spf entry
                if "	TXT	" in line:
                    continue
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


ip_addresses = []

filenames = args.addresses
for filename in filenames:
    with open(filename) as f:
        for line in f.readlines():
            ip_matches = re.findall(ipv4_pattern, line.strip('\n'))
            for ip in ip_matches:
                if ip not in ip_addresses:
                    ip_addresses.append(ip)

for ip in ip_addresses:
    if ip not in dictionary.keys():
        dictionary[ip] = ''

for key, value in sorted(dictionary.items()):
    print(key)
    for domain in value:
        print(f'\t{domain}')
