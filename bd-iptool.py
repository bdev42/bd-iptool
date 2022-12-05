#!/usr/bin/python3
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
        return 'Unknown'
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
        print(f"Address Type: {self.get_address_type()}")

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
                ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
                raise argparse.ArgumentTypeError(f"Failed to convert the {ordinal(i+1)} octet to a number: '{octet}'")
        # finally return a new IPAddress object
        return IPAddress(octet_values, prefix)

parser = argparse.ArgumentParser(description="A tool for working with IP adresses. Certifiably better than a KdG calculator.*")
parser.add_argument('-v','--version',action='version',version='%(prog)s - v'+_CURRENT_VERSION)

subcommands = parser.add_subparsers(dest='func')

parser_convert = subcommands.add_parser('convert',description="Convert ip adresses between dotted decimal and binary format.")
parser_convert.add_argument('-d', metavar='ip-address', dest='ipaddr', type=IPAddress.from_dotted_decimal)
parser_convert.add_argument('-b', metavar='ip-address', dest='ipaddr', type=IPAddress.from_dotted_binary)

parser_subnet = subcommands.add_parser('subnet',description="Split a network into subnets according to the given requirements.")
parser_subnet.add_argument('ipaddr', metavar='ip-address', type=IPAddress.from_dotted_decimal)
parser_subnet.add_argument('-s', '--required-subnets', )
parser_subnet.add_argument('requiredHosts', type=int, nargs='+')

def convert(args):
    print("--- CONVERT ---")
    print(args)
    print(f'DECIMAL: {repr(args.ipaddr)}')
    print(f'BINARY: {args.ipaddr.get_binary()}')

def subnet(args):
    print("--- IP CHARACTERISTICS ---")
    args.ipaddr.print_characteristics()
    print("--- SUBNETTING ---")
    print(args)
    requiredHosts = sorted(args.requiredHosts, reverse=True)
    currNw = args.ipaddr.get_network_address()
    numIps = 0
    hostBits = []
    bitsToBorrow = []
    print('{:3s}|{:2s}|{:15s}|{:17s}|{:17s}|{:8s}|'.format('SN#', 'bB', 'new subnet mask', 'network address', 'broadcast address', '# of IPs'))
    for i, rh in enumerate(requiredHosts):
        hostBits.append(math.ceil(math.log(rh+2, 2)))
        bitsToBorrow.append(32-(args.ipaddr.prefix + hostBits[i]))
        currNw = IPAddress((currNw + numIps).value, args.ipaddr.prefix + bitsToBorrow[i])
        numIps = 2 ** hostBits[i]
        sameNetCheck = '❌'
        if args.ipaddr.get_network_address() == IPAddress(currNw.value, args.ipaddr.prefix).get_network_address():
            sameNetCheck = '✔️'

        print('{:3d}|{:2d}|{:15s}|{:17s}|{:17s}|{:8d}|{:1s}'.format(i+1, bitsToBorrow[i], currNw.get_subnet_mask(), str(currNw.get_network_address()), str(currNw.get_broadcast_address()), numIps, sameNetCheck))

if __name__=='__main__':
    parsedArgs = parser.parse_args()
    locals()[parsedArgs.func](parsedArgs)
