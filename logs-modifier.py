#!/usr/bin/python3

import os
import re
import sys
import argparse

comment=" File has been modified according to the github project (https://github.com/abletsoff/logs_modifier) "

# =============== Functions ===============

def substitution(data, regex_str, name, excl_regex_str, detailed=False):
    
    regex = re.compile(regex_str)
    excl_regex = re.compile(excl_regex_str)

    # value.group(0)    - matching string value
    # value.span()      - position in text where matching string is

    match_values = {(x.group(0), x.span()) for x in re.finditer(regex, data)}
    excl_values = {(x.group(0), x.span()) for x in re.finditer(excl_regex, data)}
    mod_values = match_values - excl_values

    indexed = {} # substitutions tracker

    for value, (left, right) in sorted(mod_values, key=lambda var: var[1][0]):
        if value not in indexed:
            indexed[value] = str(len(indexed) + 1) 
        sub_value = (name + '_' + indexed[value]).center(right - left, '*')         
        data = data[:left] + sub_value + data[right:]
        if detailed == True:
            print('\t', value, '=>', sub_value)

    return data

def arg_parser():
    
    parser = argparse.ArgumentParser(description=' CLI logs modifier '.center(50,'='))
    parser.add_argument('-m', '--mac', action='store_true', help='modify MAC addresses')
    parser.add_argument('-4', '--ipv4', action='store_true', help='modify IPv4 addresses')
    parser.add_argument('-6', '--ipv6', action='store_true', help='modify IPv6 addresses')
    parser.add_argument('-H', '--hash', action='store_true', help='modify salted hashes')
    parser.add_argument('-p', '--print', action='store_true', help='print result to stdout')
    parser.add_argument('-r', '--regex', action='store', help="user defined regex to modify")
    parser.add_argument('-P', '--pass_regex', action='store', help="user defined regex to not modify")
    parser.add_argument('-d', '--detail', action='store_true', help="display information about modified values")
    parser.add_argument('-R', '--remove', action='store_true', help="remove original file")
    parser.add_argument('path', metavar='PATH', type=str, nargs='+', help='path for modification procedures')

    return parser.parse_args()
    
def modify_file(file_name, args):
    
    try:
        f = open(file_name)
        try: 
            data = f.read()
        except UnicodeDecodeError as excp:
            print(f'UnicodeDecodeError: {file_name}')
            f.close()
            return
        f.close()
   
        if args.remove == True:
            os.remove(file_name)
        if args.pass_regex == None:
            args.pass_regex = r'$a'     # meaningless regex 
        if args.detail == True:
            print(f"Substitutions in '{file_name}': ")
        if args.mac == True: 
            data = substitution(data, regex_MAC, 'MAC', rf'({regex_MAC_excl})|({args.pass_regex})', args.detail) 
        if args.ipv4 == True: 
            data = substitution(data, regex_IPv4, 'IPv4', rf'({regex_IPv4_excl})|({args.pass_regex})', args.detail) 
        if args.ipv6 == True: 
            data = substitution(data, regex_IPv6, 'IPv6', rf'({regex_IPv6_excl})|({args.pass_regex})', args.detail) 
        if args.hash == True: 
            data = substitution(data, regex_Salted_Hashes, 'Salted_Hash', args.pass_regex, args.detail)  
        if args.regex != None:
            data = substitution(data, args.regex, 'U', args.pass_regex, args.detail) 
        if args.detail == True:
            print()
        if args.print == True:
            print(data)
        
        f = open(file_name + '.modified', "w")
        f.write('#' + '-' * len(comment) + '#\n')
        f.write('#' + comment + '#\n')
        f.write('#' + '-' * len(comment) + '#\n\n')
        f.write(data)
        f.close

    except PermissionError as excp:
        print(excp)

# =============== Regular Expressions ===============

regex_MAC = (   r'(([0-9a-fA-F]{2}[:.-]){5}'
                r'[0-9a-fA-F]{2})|'
                r'(([0-9a-fA-F]{4}[-.]){2}'
                r'[0-9a-fA-F]{4})')

# Exclude Broadcast MAC address from substitution
regex_MAC_excl = (  r'(([fF]{2}[:.-]){5}'
                    r'[fF]{2})|'
                    r'(([fF]{4}[-.]){2}'
                    r'[fF]{4})')


regex_IPv4 = (  r'([1-2]?\d{1,2}\.){3}'
                r'[1-2]?\d{1,2}')

# Exclude Loopback, Broadcast addresses and mostly masks
regex_IPv4_excl = ( r'(127\.0\.0\.1)|'
                    r'(255\.([1-2]?\d{1,2}\.){2}'
                    r'[1-2]?\d{1,2})')

# This is monster "https://ihateregex.io/expr/ipv6/"
regex_IPv6 = r'''(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))'''

# Exclude Loopback
regex_IPv6_excl = r'::1'

# Salted hashes
regex_Salted_Hashes =  r'\$2[abyx]\$\d\d\$.{53}' #bcrypt 

# =============== Program Logic ===============

args = arg_parser()

for path in args.path:
    try:
        if os.path.isfile(path):
            modify_file(path, args) 
        elif os.path.isdir(path):
            for root,d_names,f_names in os.walk(path):
                for f_name in f_names:
                    modify_file(f"{root}/{f_name}", args)
        else:
            raise FileNotFoundError(f"[Errno 2] No such file or directory: '{path}'")

    except FileNotFoundError as excp:
        print(excp)
