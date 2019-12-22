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
    client_nodes = [{"id" : client['_id'], "group": 5} for client in db.client.find()]
    nodes = ap_nodes + client_nodes

    # links
    links = [{"source" : ap['ap'], "target": client['_id'], "value": 10}
             for client in db.client.find()
             for ap in client['ap']]
    valid_nodes = [node["id"] for node in nodes]
    valid_nodes = list(filter(None, valid_nodes)) #filter empty string

    links = list(filter(lambda link: link["source"] in valid_nodes and link["target"] in valid_nodes, links))

    return jsonify({'nodes': ap_nodes+client_nodes, 'links' : links})

@app.route('/')
def index():
    return render_template('./index.html')


if __name__ == '__main__':
    app.run(debug=True)
