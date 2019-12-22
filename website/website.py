#!/usr/bin/env python3

from flask import Flask, jsonify,render_template
from flask import abort
import json
from pymongo import MongoClient
from pprint import pprint

app = Flask(__name__)

mongodb = MongoClient("mongodb://localhost/networks")
db = mongodb.networks

@app.route('/rest/', methods=['GET'])
def rest():
    # nodes
    ap_nodes = [{"id" : ap['ssid'], "group" : 1} for ap in db.ap.find()]
    client_nodes = [{"id" : client['_id'], "group": 2} for client in db.client.find()]
    nodes = ap_nodes + client_nodes

    # links
    links = [{"source" : ap['ap'], "target": client['_id'], "value": 10}
             for client in db.client.find()
             for ap in client['ap']]
    valid_nodes = [node["id"] for node in nodes]
    valid_nodes = list(filter(None, valid_nodes)) #filter empty string

    
    unknown_source_nodes =  [{"id" : link['source'], "group" : 3} for link in links if link["source"] not in valid_nodes]
    unknown_target_nodes =  [{"id" : link['target'], "group" : 4} for link in links if link["target"] not in valid_nodes]    

    links = list(filter(lambda link: len(link["source"]) and len(link["target"]), links))

    nodes = nodes + unknown_source_nodes + unknown_target_nodes
    nodes = list(filter(lambda node: len(node["id"]), nodes))    
    
    return jsonify({'nodes': nodes, 'links' : links})

@app.route('/')
def index():
    return render_template('./index.html')


if __name__ == '__main__':
    app.run(debug=True)
