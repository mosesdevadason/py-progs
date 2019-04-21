"""Packet generator tool."""

import argparse
from scapy.all import Ether, Dot1Q, sendpfast
import netaddr

PKT_GEN_DESC = """Packet generator tool."""
VLAN_MAX_LIMIT = 4000
DEFAULT_INPUT_CFG_FILE = 'input.txt'
DEFAULT_IFACE = 'eth0'

def __inc_mac(mac_str):
    mac_int = int(netaddr.EUI(mac_str))
    mac_int = mac_int + 1
    return str(netaddr.EUI(mac_int)).lower().replace('-', ':')

def __inc_vlan(vlan):
    if vlan == VLAN_MAX_LIMIT:
        return 1
    return vlan + 1

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

    def __create_packets(self):
        pkts = []
        srcmac_str = self.l2fields['srcmac']
        dstmac_str = self.l2fields['dstmac']
        vlan = self.l2fields['vlan']
        index = 0
        while index < self.totpkts:
            pkt = Ether(src=srcmac_str, dst=dstmac_str)
            if self.l2fields_inc['srcmac']:
                srcmac_str = __inc_mac(srcmac_str)
                print('Souce MAC : %s' % srcmac_str)
            if self.l2fields_inc['dstmac']:
                dstmac_str = __inc_mac(dstmac_str)
                print('Destination MAC : %s' % dstmac_str)
            if vlan != 0:
                pkt = pkt / Dot1Q(vlan=vlan)
                if self.l2fields_inc['vlan']:
                    vlan = __inc_vlan(vlan)
            pkt = pkts.append(pkt)
            index = index + 1
        return pkts

    def send_pkt(self):
        """Sends packets as per the provided parameters."""
        pkts = self.__create_packets()
        sendpfast(pkts, pps=self.pps, iface=self.iface)

def read_params(filename=DEFAULT_INPUT_CFG_FILE):
    """Reads the stream related params present in the input configuration file.
    filename: Name of the configuration file."""
    params = {}
    with open(filename) as streamfile:
        for line in streamfile:
            (key, val) = line.split('=')
            key = key.strip()
            val = val.strip()
            if key in ('vlan', 'totpkts', 'pps'):
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
    params = read_params()
    pktgen = Pktgen(params)

if __name__ == '__main__':
    __main()
