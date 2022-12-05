#!/usr/bin/env python3
# https://github.com/boldi-kdg/bd-iptool #
_CURRENT_VERSION = '1.0'

import argparse
import math

def bitwise_and(abytes, bbytes):
    return bytes([a & b for a, b in zip(abytes[::-1], bbytes[::-1])][::-1])

def bitwise_or(abytes, bbytes):
    return bytes([a | b for a, b in zip(abytes[::-1], bbytes[::-1])][::-1])

def bitwise_not(abytes):
    return bytes([a ^ 255 for a in abytes[::-1]][::-1])


class IPAddress:
    value: bytes = bytes([0,0,0,0])
    prefix: int = None

    def __init__(self, address: bytes, prefix: int=0) -> None:
        self.value = bytes(address)
        if prefix == 0:
            self.prefix = self.get_prefix_based_on_class()
        else:
            self.prefix = prefix
    
    def __str__(self) -> str:
        return f'{self.value[0]}.{self.value[1]}.{self.value[2]}.{self.value[3]}/{self.prefix}'
    
    def __repr__(self) -> str:
        return f'{self.value[0]}.{self.value[1]}.{self.value[2]}.{self.value[3]}'
    
    def __eq__(self, o: object) -> bool:
        if isinstance(o, IPAddress):
            #print(str(self) + " " + str(o))
            return self.value[0] == o.value[0] and self.value[1] == o.value[1] and self.value[2] == o.value[2] and self.value[3] == o.value[3]
        return False
    
    
    def __add__(self, num: int):
        #self.value = int.to_bytes(int.from_bytes(self.value, 'big', signed=False) + num, 4, 'big', signed=False)
        n1, n2, n3, n4 = int.to_bytes(num, 4, 'big', signed=False)
        #print([n1, n2, n3, n4])

        oct4 = (self.value[3] + n4) % 256
        carr = math.floor((self.value[3] + n4) / 255)
        oct3 = (self.value[2] + n3 + carr) % 256
        carr = math.floor((self.value[2] + n3 + carr) / 255)
        oct2 = (self.value[1] + n2 + carr) % 256
        carr = math.floor((self.value[1] + n2 + carr) / 255)
        oct1 = (self.value[0] + n1 + carr) % 256
        carr = math.floor((self.value[0] + n1 + carr) / 255)
        if carr > 0:
            raise OverflowError
        return IPAddress(bytes([oct1, oct2, oct3, oct4]), self.prefix)
    
    '''
    def __sub__(self, num: int):
        self.value = int.to_bytes(int.from_bytes(self.value, 'big', signed=False) - num, 4, 'big', signed=False)
    
    def __gt__(self, __o: object):
        if isinstance(__o, IPAddress):
            return int.from_bytes(self.value, 'big', signed=False) > int.from_bytes(__o.value, 'big', signed=False)
        return False
    
    def __lt__(self, __o: object):
        if isinstance(__o, IPAddress):
            return int.from_bytes(self.value, 'big', signed=False) < int.from_bytes(__o.value, 'big', signed=False)
        return False
    '''

    def get_prefix_based_on_class(self) -> int:
        if self.value[0] >= int('0b0000_0000', base=0) and self.value[0] <= int('0b0111_1111', base=0):
            #Class A
            return 8
        elif self.value[0] >= int('0b1000_0000', base=0) and self.value[0] <= int('0b1011_1111', base=0):
            #Class B
            return 16
        elif self.value[0] >= int('0b1100_0000', base=0) and self.value[0] <= int('0b1101_1111', base=0):
            #Class C
            return 24
        else:
            # default to Class C
            return 24
    
    def get_default_class(self) -> str:
        if self.value[0] >= int('0b0000_0000', base=0) and self.value[0] <= int('0b0111_1111', base=0):
            return 'Class A'
        elif self.value[0] >= int('0b1000_0000', base=0) and self.value[0] <= int('0b1011_1111', base=0):
            return 'Class B'
        elif self.value[0] >= int('0b1100_0000', base=0) and self.value[0] <= int('0b1101_1111', base=0):
            return 'Class C'
        elif self.value[0] >= int('0b1110_0000', base=0) and self.value[0] <= int('0b1110_1111', base=0):
            return 'Class D (Multicast or Experimental) [WARNING: Currently handled by the tool as Class C]'
        elif self.value[0] >= int('0b1111_0000', base=0) and self.value[0] <= int('0b1111_1111', base=0):
            if self.value[0] == 255 and self.value[1] == 255 and self.value[2] == 255 and self.value[3] == 255:
                return 'BROADCAST (Unique adress, would fall under Class E technically) [WARNING: Currently handled by the tool as Class C]'
            return 'Class E (Experimental) [WARNING: Currently handled by the tool as Class C]'
        else:
            return 'Unknown'
    
    def get_binary(self):
        res = ''
        for i, byte in enumerate(self.value):
            n = byte
            for bit in range(8, 0, -1):
                if n >= 2**(bit-1):
                    res += '1'
                    n -= 2**(bit-1)
                else:
                    res += '0'
                if bit == 5:
                    res += ' '
            if i < len(self.value) - 1:
                res += '.'
        return res
    
    @staticmethod
    def get_subnet_mask_bytes(prefix: int):
        return bytes([
            int(f"0b{'1'*(min(prefix, 8))}{'0'*(8-min(prefix, 8))}", base=0),
            int(f"0b{'1'*(min(prefix-8, 8))}{'0'*(8-min(prefix-8, 8))}", base=0),
            int(f"0b{'1'*(min(prefix-16, 8))}{'0'*(8-min(prefix-16, 8))}", base=0),
            int(f"0b{'1'*(min(prefix-24, 8))}{'0'*(8-min(prefix-24, 8))}", base=0)
        ])
    
    def get_subnet_mask(self):
        mask = IPAddress.get_subnet_mask_bytes(self.prefix)
        return f'{mask[0]}.{mask[1]}.{mask[2]}.{mask[3]}'

    def get_network_address(self):
        mask = IPAddress.get_subnet_mask_bytes(self.prefix)
        return IPAddress(bitwise_and(mask, self.value), self.prefix)
    
    def get_broadcast_address(self):
        nwaddr = self.get_network_address().value
        invmask = bitwise_not(IPAddress.get_subnet_mask_bytes(self.prefix))
        return IPAddress(bitwise_or(nwaddr, invmask), self.prefix)
    
    def get_address_type(self):
        return 'Unknown (WIP)'
        nwaddr = self.get_network_address()
        bcaddr = self.get_broadcast_address()
        if self == nwaddr:
            return 'Network'
        elif self == bcaddr:
            return 'Broadcast'
        elif self == nwaddr+1:
            return 'First Host'
        elif self == bcaddr-1:
            return 'Last Host'
        elif self > nwaddr and self < bcaddr:
            return 'Host'
        else:
            return 'Unknown'

    def print_characteristics(self):
        print(f"Address: {str(self)}")
        print(f"Network Address: {str(self.get_network_address())}")
        print(f"Broadcast Address: {str(self.get_broadcast_address())}")
        print(f"Subnet Mask: {self.get_subnet_mask()}")
        print(f"Default Class: {self.get_default_class()}")

    @staticmethod
    def from_dotted_binary(arg: str):
        arg = arg.replace(' ', '') # remove extra spaces, if present
        #find the 4 octets
        octets = arg.split('.')
        if len(octets) != 4:
            raise argparse.ArgumentTypeError(f"IPv4 address must have 4 octets (received: {len(octets)})")
        # convert octet binary strings into bytes
        octet_values = bytearray([0,0,0,0])
        
        for i, octet in enumerate(octets):
            bitsLeft = 8
            num = 0
            bitsMissing = True
            for c in octet:
                if c == '1':
                    num += 2**(bitsLeft-1)
                    bitsLeft-=1
                elif c == '0':
                    bitsLeft-=1
                if bitsLeft <= 0:
                    bitsMissing = False
                    break
            if bitsMissing:
                raise argparse.ArgumentTypeError(f"Missing bits from octet #{i+1}. There must be 8 bits in each octet/byte.")
            octet_values[i] = num
        # finally return a new IPAddress object
        return IPAddress(octet_values)
            
    
    @staticmethod
    def from_dotted_decimal(arg: str):
        arg = arg.replace(' ', '') # remove extra spaces, if present
        #check for prefix
        prefix = 0
        if arg.count('/') > 0:
            parts = arg.split('/')
            if len(parts) != 2:
                raise argparse.ArgumentTypeError("Make sure there is only one '/' when using a prefix (format like: 0.0.0.0/0)")
            arg = parts[0]
            prefix = parts[1]
            #try to get prefix value
            try:
                val = int(prefix)
                if val != 0 and (val < 8 or val > 30):
                    raise argparse.ArgumentTypeError(f"Invalid prefix: '/{val}' (must be in range 8-30 or 0 to auto-assign).")
                prefix = val
            except ValueError:
                raise argparse.ArgumentTypeError(f"Failed to convert the prefix to a number: '/{prefix}'")
        #find the 4 octets
        octets = arg.split('.')
        if len(octets) != 4:
            raise argparse.ArgumentTypeError(f"IPv4 address must have 4 octets (received: {len(octets)})")
        # convert octet strings into bytes (numbers)
        octet_values = bytearray([0,0,0,0])
        for i, octet in enumerate(octets):
            try:
                val = int(octet)
                if val < 0 or val > 255:
                    raise argparse.ArgumentTypeError(f"All octets must be in the unsigned byte range (0-255).\n Octet #{i+1} is outside this range with the value of: {val}")
                octet_values[i] = val
            except ValueError:
                raise argparse.ArgumentTypeError(f"Failed to convert octet #{i+1} to a number: '{octet}'")
        # finally return a new IPAddress object
        return IPAddress(octet_values, prefix)

parser = argparse.ArgumentParser(description="A tool for working with IP adresses. Certifiably better than a KdG calculator.*")
parser.add_argument('-v','--version',action='version',version='%(prog)s - v'+_CURRENT_VERSION)

subcommands = parser.add_subparsers(dest='func')

parser_convert = subcommands.add_parser('convert',description="Convert ip adresses between dotted decimal and binary format.")
parser_convert.add_argument('-d', metavar='ip-address', dest='ipaddr', type=IPAddress.from_dotted_decimal)
parser_convert.add_argument('-b', metavar='ip-address', dest='ipaddr', type=IPAddress.from_dotted_binary)

parser_subnet = subcommands.add_parser('subnet',description="Split a network into subnets according to the given requirements.", epilog='''
table columns:
Hb = host bits required, this is calculated from requiredHosts;
Bb = the bits borrowed, aka. additional subnet bits required;
# of IPs = yes this is the number of IPs on this subnet,
  KEEP IN MIND: 2 of these IPs are not usable for hosts (network address & host address);
InR = in range, if its a cross it indicates the subnet is not part of the original network, 
  meaning you ran out of IP adresses and cannot make more subnets (you may still try smaller subnets.);
''')
parser_subnet.add_argument('ipaddr', metavar='ip-address', type=IPAddress.from_dotted_decimal)
parser_subnet.add_argument('-F', action='store_true', default=False, dest='fixedLength', help='fixed length subnetting: make subnets with length requiredHosts[0] until a subnet is out of range')
parser_subnet.add_argument('-s', action='store_true', default=False, dest='subnetsInsteadOfHosts', help='requiredHosts will be interpreted as requiredSubnets instead')
parser_subnet.add_argument('requiredHosts', type=int, nargs='+')

def convert(args):
    print("--- CONVERT ---")
    #print(args)
    if args.ipaddr == None:
        print(" You must specify the ip address to convert, in binary with -b or in decimal with -d.")
        return
    
    print(f'DECIMAL: {repr(args.ipaddr)}')
    print(f'BINARY: {args.ipaddr.get_binary()}')
    print("--- IP CHARACTERISTICS ---")
    args.ipaddr.print_characteristics()

def subnet(args):
    print("--- IP CHARACTERISTICS ---")
    args.ipaddr.print_characteristics()
    print("--- SUBNETTING ---")
    #print(args)
    currNw = args.ipaddr.get_network_address()
    numIps = 0
    print('{:3s}|{:2s}|{:2s}|{:15s}|{:18s}|{:18s}|{:8s}|{:8s}|{:3s}'.format('SN#', 'Hb', 'Bb', 'new subnet mask', 'network address', 'broadcast address', '# of IPs', '# of SNs', 'InR'))
    if args.fixedLength:
        i = 0
        passedCheck = True
        while passedCheck:
            currNw, numIps, passedCheck = subnet_gensubnet(args, i+1, args.requiredHosts[0], currNw, numIps)
            i+=1
    else:
        requiredHosts = sorted(args.requiredHosts, reverse=(not args.subnetsInsteadOfHosts))
        for i, rh in enumerate(requiredHosts):
            currNw, numIps, _ = subnet_gensubnet(args, i+1, rh, currNw, numIps)
        
def subnet_gensubnet(args, sn: int, rh: int, currNw: IPAddress, numIps: int):
    if args.subnetsInsteadOfHosts:
        bitsToBorrow = math.ceil(math.log(rh, 2))
        hostBits = 32-(args.ipaddr.prefix + bitsToBorrow)
    else:
        hostBits = math.ceil(math.log(rh+2, 2))
        bitsToBorrow = 32-(args.ipaddr.prefix + hostBits)
    currNw = IPAddress((currNw + numIps).value, args.ipaddr.prefix + bitsToBorrow)
    numIps = 2 ** hostBits
    numSNs = 2 ** bitsToBorrow
    sameNetCheck = '❌'
    inRange = False
    if args.ipaddr.get_network_address() == IPAddress(currNw.value, args.ipaddr.prefix).get_network_address():
        sameNetCheck = '✔️'
        inRange = True
    
    print('{:3d}|{:2d}|{:2d}|{:15s}|{:18s}|{:18s}|{:8d}|{:8d}|{:3s}'.format(sn, hostBits, bitsToBorrow, currNw.get_subnet_mask(), str(currNw.get_network_address()), str(currNw.get_broadcast_address()), numIps, numSNs, sameNetCheck))
    return (currNw, numIps, inRange)


if __name__=='__main__':
    parsedArgs = parser.parse_args()
    if parsedArgs.func not in ('convert', 'subnet'):
        parser.print_help()
    else:
        locals()[parsedArgs.func](parsedArgs)
