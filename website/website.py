#!/usr/bin/env python3

from flask import Flask, jsonify,render_template,request
from flask import abort
import json
from pymongo import MongoClient
from pprint import pprint
from datetime import datetime

app = Flask(__name__)

mongodb = MongoClient("mongodb://localhost/networks")
db = mongodb.networks

def last_seen(timestamp):
    last = datetime.fromtimestamp(timestamp)
    now = datetime.now()
    delta = now - last
    hours = (24*3600 - delta.seconds) // 3600
    minutes = (24*3600 - delta.seconds) // 60
    days = delta.days
    if days > 0:
        return "{} days".format(days)
    elif hours > 0:
        return "{} hours".format(hours)
    else:
        return "{} minutes".format(minutes)

@app.route('/rest/', methods=['GET'])
def rest():
    # known AP
    ap_nodes = [{'id' : ap['ssid'],
                 'mac' : ap['_id'],
                 'ssid' : ap['ssid'],
                 'alias' : ap['alias'] if 'alias' in ap else "",
                 'crypto' : ap['crypto'] if 'crypto' in ap else "",
                 'signal' : ap['signal'] if 'signal' in ap else "",
                 'lastSeen' : last_seen(ap['lastSeen']) if 'lastSeen' in ap else "",
                 'channel' : ap['channel'] if 'channel' in ap else "",
                 'group' : 1}
                for ap in db.ap.find()]
    # known Client
    client_nodes = [{'id' : client['_id'],
                     'mac' : client['_id'],
                     'alias' : client['alias'] if 'alias' in client else "",
                     'signal' : client['signal'] if 'signal' in client else "",
                     'lastSeen' : last_seen(client['lastSeen']) if 'lastSeen' in client else "",
                     'alias' : client['alias'] if 'alias' in client else "",
                     'group': 2}
                    for client in db.client.find()]
    
    known_nodes = [node["id"] for node in ap_nodes + client_nodes]
    known_nodes = list(filter(None, known_nodes)) #filter empty string

    
    links = [{"source" : ap['ap'], # always a SSID
              "target": client['_id'], # always a MAC
              "value": 10}
             for client in db.client.find()
             for ap in client['ap']]
    
    unknown_ap_nodes =  [{"id" : link['source'],
                          'signal' : "",
                          "ssid" : link['source'], "group" : 3}
                         for link in links if link["source"] not in known_nodes]

    nodes = ap_nodes + client_nodes + unknown_ap_nodes

    # filter all empty SSID 
    nodes = list(filter(lambda node: "ssid" not in node or len(node["ssid"]), nodes))
    links = list(filter(lambda link: len(link["source"]) and len(link["target"]), links))    
    return jsonify({'nodes': nodes, 'links' : links})


@app.route('/alias', methods=['PUT'])
def alias():
    print(request.data)
    return jsonify({'alias' : "nix"})

@app.route('/')
def index():
    return render_template('./index.html')


if __name__ == '__main__':
    app.run(debug=True)
