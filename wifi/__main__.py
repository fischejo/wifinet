#!/usr/bin/env python3

from scapy.all import *
import pyric.pyw as pyw
from multiprocessing import Process,Array
from time import sleep
from random import choices
from pymongo import MongoClient
from pprint import pprint
from systemd import journal
import argparse

CHANNEL_COUNT = 13
MONGO_DB = "mongodb://localhost/networks"

#ap = []
client = []
channel_weights = Array('i', [1]*CHANNEL_COUNT)


"""A little-endian short field that converts from mhz to channel"""
def m2i(x):
    return int(min(14, max(1, (x - 2407) / 5)))

def scan(iface, channel_weights, mongodb_url) :
    mongodb = MongoClient(mongodb_url)
    db = mongodb.networks
    
    def Packet_info(pkt):
        # finding APs by Beacons (subtype == 8)
        if pkt.haslayer(Dot11Beacon) :
            db.ap.update({'_id' : pkt.addr2},
                         {"$set":{'ssid' : pkt.info.decode("utf-8")}},
                         upsert=True)

        # finding corresponding clients by Probes
        if pkt.haslayer(Dot11ProbeReq) :
            channel = m2i(pkt[RadioTap].ChannelFrequency)
            channel_weights[channel-1] += 1
            ap = {'ap' : pkt.info.decode("utf-8")}
            db.client.update({'_id' : str(pkt.addr2)},
                             {
                                 '$addToSet' : { 'ap': ap },
#                                 '$addToSet' : { 'channel': channel },
                             },
                             upsert=True)
    journal.write("Start sniffing on interface {}".format(iface))
    sniff(iface = iface, prn = Packet_info)


if __name__ == '__main__':
    # parse arguments
    parser = argparse.ArgumentParser(prog="python3 -m wifi", description='Wifinet Sniffer')
    parser.add_argument('-i', '--iface', required=True, help="Interface of Wifi Card")
    parser.add_argument('-m', '--mongodb', default=MONGO_DB, help="Default: {}".format(MONGO_DB))
    args = parser.parse_args()

    # set card into monitor mode
    pyw_card = pyw.getcard(args.iface)
    pyw.down(pyw_card)
    pyw.modeset(pyw_card, 'monitor')
    pyw.up(pyw_card)
    journal.write("Interface {} set to promiscuous mode".format(args.iface))
    
    # start scanning
    p = Process(name='crawler',target=scan, args=(args.iface,channel_weights, args.mongodb))
    p.start()

    journal.write("Start channel hopping on interface {}".format(args.iface))
    while(True):
        weights = list(channel_weights)
        channels = list(range(1,CHANNEL_COUNT+1))
        ch = choices(channels,weights)[0]    
        pyw.chset(pyw_card, ch, None)
        sleep(0.5)

