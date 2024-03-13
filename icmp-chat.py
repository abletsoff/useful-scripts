import socket
import re
import sys
import struct
import logging
import argparse

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
IPv4_REGEX = re.compile(r'^([1-2]?\d{1,2}\.){3}[1-2]?\d{1,2}$')

class ICMP:

    def check_ip(host):

        if IPv4_REGEX.match(host):
            return True
        else:
            try:
                socket.gethostbyname(host)
                return True
            except socket.gaierror as excp:
                logging.warning(f"Domain name '{host}' does not known")
                return False

    def __init__(self, type, opcode, payload=b'Hello friend:)', listen_all_icmp=False):
        
        self.type = type
        self.opcode = opcode
        
        if type == 8: #ECHO request
            self.id = 1 
            self.seq_num = 256
        else:
            self.id = 0 
            self.seq_num = 0

        self.payload = payload

        # stupid header generation, but it`s work
        self.checksum = 0
        self.header = self.header_gen()
        self.checksum = self.checksum_gen()
        self.header = self.header_gen()
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_RAW,
                        socket.getprotobyname("icmp"))
        
        self.listen_all_icmp = listen_all_icmp

    def header_gen(self):

        return struct.pack('BBHHH', self.type, self.opcode, 
                self.checksum, self.id, self.seq_num)

    def checksum_gen(self):
        # https://datatracker.ietf.org/doc/html/rfc1071 
        # https://github.com/certator/pyping
       
        data = self.header_gen() + self.payload
        checksum = 0

        if len(data) % 2:
            if sys.byteorder == 'little':
                data += struct.pack('B', 0)
            else:
                data = data[:-1] + struct.pack('B', 0) + data[-1:]

        tup_iter = ((data[i + 1], data[i]) if sys.byteorder == 'little' 
                else (data[i], data[i + 1]) for i in range(0, len(data), 2))

        for h_byte, l_byte in tup_iter:
           checksum += h_byte * 256 + l_byte
        
        checksum = (checksum >> 16) + (checksum & 0xffff)
        checksum += (checksum >> 16)
        checksum = ~checksum & 0xffff

        return checksum

    def transmit(self, host='127.0.0.1'):
        
        if ICMP.check_ip(host):
            port_num = 1 # does not matter for ICMP
            self.sock.sendto(self.header + self.payload, (host, port_num))
            logging.info(f"Sending {len(self.payload)} byte(s) to '{host}'")

    def recive(self, address, file): 
       
        try:
            port_num = 1 # does not matter for ICMP
            self.sock.bind(('0.0.0.0', port_num))
            raw_bytes, address_tup = self.sock.recvfrom(args.size + 28)
            ip_header, icmp_header, payload = raw_bytes[:20], raw_bytes[20:28], raw_bytes[28:]
            
            if self.listen_all_icmp or (icmp_header[0] == self.type and icmp_header[1] == self.opcode): 
                
                if not address or address_tup[0] == address: 
                    logging.info(f'Reciving {len(payload)} byte(s) from {address_tup[0]}')
                 
                    if file: 
                        file.write(payload)
                    else:
                        print(payload.decode('utf-8'))

        except KeyboardInterrupt:
            sys.exit()
        except UnicodeDecodeError as excp:
            logging.warning(excp)

def args_parse():
    
    parser = argparse.ArgumentParser(description=' ICMP Chat '.center(50,'='))
    parser.add_argument('-f', '--filename', type=str, help='filename to transmit / recive')
    parser.add_argument('-t', '--text', type=str, help='text string to transmit', default='')
    parser.add_argument('-H', '--host', type=str, help='host to transmit / listen from', default='127.0.0.1')
    parser.add_argument('-l', '--listen', action='store_true', help='listen mode')
    parser.add_argument('-L', '--logging', action='store_true', help='Detailed logging')
    # mtu (1500) - ip_header(20) - icmp_header(8) = 1472 trying to avoid ip fragmentation
    parser.add_argument('-s', '--size', type=int, help='max size of payload for one icmp packet', default=1472)
    parser.add_argument('-T', '--type', type=int, help='icmp type', default=8)
    parser.add_argument('-O', '--opcode', type=int, help='icmp opcode', default=0)
    parser.add_argument('-A', '--all_icmp', action='store_true', help='listen for all ICMP types and opcodes. \
            Do not use this option while listening ECHO request') 

    return parser.parse_args()
    
if __name__ == '__main__':
    args = args_parse()
    
    if not args.logging:
        logging.disable('INFO')

    if args.listen:

        icmp = ICMP(args.type, args.opcode, listen_all_icmp=args.all_icmp)
        file = None
        if args.filename:
            file = open(args.filename, 'wb')
        while True:
            icmp.recive(args.host, file)
    
    else:
        payload = bytes(args.text, 'utf-8')
        try:
            if args.filename:
                with open(args.filename, 'rb') as file:
                    payload += file.read() 
        except FileNotFoundError as excp:
            logging.warning(excp)
        finally:
            for payload_chunk in [payload[i:i+args.size] for i in range(0,len(payload),args.size)]:
                icmp = ICMP(args.type, args.opcode, payload_chunk)
                icmp.transmit(args.host)
