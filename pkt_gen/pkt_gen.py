"""Packet generator tool."""

from scapy.all import Packet, Ether, Dot1Q, sendpfast, StrLenField
import argparse
import utils as util

PKT_GEN_DESC = """Packet generator tool."""
VLAN_MAX_LIMIT = 4000
DEFAULT_INPUT_CFG_FILE = 'input.txt'
DEFAULT_IFACE = 'eth0'
DEFAULT_LEN = 64

def _inc_mac(mac_str):
    mac_int = util.mac_str_to_int(mac_str)
    mac_int = mac_int + 1
    return util.mac_int_to_str(mac_int)

def _inc_vlan(vlan):
    if vlan == VLAN_MAX_LIMIT:
        return 1
    return vlan + 1

class L2Payload(Packet):
    """L2 dummy payload."""
    name = 'l2payload'
    fields_desc = [StrLenField('_l2payload', '\x01' * DEFAULT_LEN, lambda pkt:pkt.len)]

class Pktgen:
    """Packet generator class."""
    def __init__(self, params):
        assert isinstance(params, dict)
        self.iface = DEFAULT_IFACE
        self.l2fields = {}
        self.l2fields_inc = {}
        self.l2fields['srcmac'] = None
        self.l2fields['dstmac'] = None
        self.l2fields['vlan'] = 0
        self.l2fields['l2payload_size'] = 0
        self.l2fields_inc['srcmac'] = False
        self.l2fields_inc['dstmac'] = False
        self.l2fields_inc['vlan'] = False
        self.totpkts = 1
        self.pps = None
        if 'iface' in params:
            self.iface = params['iface']
        if 'srcmac' in params:
            self.l2fields['srcmac'] = params['srcmac']
        if 'dstmac' in params:
            self.l2fields['dstmac'] = params['dstmac']
        if 'inc_srcmac' in params:
            self.l2fields_inc['srcmac'] = params['inc_srcmac']
        if 'inc_dstmac' in params:
            self.l2fields_inc['dstmac'] = params['inc_dstmac']
        if 'vlan' in params:
            self.l2fields['vlan'] = params['vlan']
            assert isinstance(self.l2fields['vlan'], int)
        if 'inc_vlan' in params:
            self.l2fields_inc['vlan'] = params['inc_vlan']
        if 'totpkts' in params:
            self.totpkts = params['totpkts']
            assert isinstance(self.totpkts, int)
        if 'pps' in params:
            self.pps = params['pps']
            assert isinstance(self.pps, int)
        if 'l2payload_size' in params:
            self.l2fields['l2payload_size'] = params['l2payload_size']
            assert isinstance(self.l2fields['l2payload_size'], int)

    def __create_packets(self):
        pkts = []
        srcmac_str = self.l2fields['srcmac']
        dstmac_str = self.l2fields['dstmac']
        vlan = self.l2fields['vlan']
        l2payload_size = self.l2fields['l2payload_size']
        if 0 == l2payload_size:
            l2payload_size = DEFAULT_LEN
        l2payload = L2Payload(_l2payload='\x01' * l2payload_size)
        for _ in range(self.totpkts):
            pkt = Ether(src=srcmac_str, dst=dstmac_str)
            if self.l2fields_inc['srcmac']:
                srcmac_str = _inc_mac(srcmac_str)
            if self.l2fields_inc['dstmac']:
                dstmac_str = _inc_mac(dstmac_str)
            if vlan != 0:
                pkt = pkt / Dot1Q(vlan=vlan)
                if self.l2fields_inc['vlan']:
                    vlan = _inc_vlan(vlan)
            pkt = pkt
            pkt = pkt / l2payload
            pkts.append(pkt)
        return pkts

    def send_pkts(self):
        """Sends packets as per the provided parameters."""
        pkts = self.__create_packets()
        sendpfast(pkts, pps=self.pps, iface=self.iface)

def read_params(filename=DEFAULT_INPUT_CFG_FILE, iface=DEFAULT_IFACE):
    """
    Reads the stream related params present in the input configuration file.
    :param filename: Name of the configuration file.
    :return: Packet generator params as a dictionary.
    """
    params = {}
    params['iface'] = 'lo'
    with open(filename) as streamfile:
        for line in streamfile:
            (key, val) = line.split('=')
            key = key.strip()
            val = val.strip()
            if key in ('vlan', 'totpkts', 'pps', 'l2payload_size'):
                assert val.isdigit()
                val = int(val)
            if key in ('inc_srcmac', 'inc_dstmac', 'inc_vlan'):
                assert val.lower() == 'yes' or val.lower() == 'no'
                val = bool(val.lower() == 'yes')
            params[key] = val
    return params

def __parse_args():
    parser = argparse.ArgumentParser(description=PKT_GEN_DESC)
    parser.add_argument('stream_file')
    parser.add_argument('iface')
    return parser.parse_args()

def __main():
    args = __parse_args()
    params = read_params(args.stream_file, args.iface)
    pkts = Pktgen(params)
    pkts.send_pkts()

if __name__ == '__main__':
    __main()
