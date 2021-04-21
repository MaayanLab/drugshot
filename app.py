import datetime
import time
import os
import io
import string
from dateutil import parser
import threading
import urllib.request
import pandas as pd
import numpy as np
import re
import requests
from collections import Counter
from flask import Flask, request, jsonify, session, send_file, redirect, render_template
from flask_cors import CORS
from flask_session import Session 

from utils import *

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

print("server started")

base_name = os.environ.get('BASE_NAME', 'drugshot')
cors = CORS(app, resources={r"/"+base_name+"/*": {"origins": "*"}})

print("init DrugRIF")

drugrif = pd.read_csv('https://appyters.maayanlab.cloud/storage/DrugShot/DrugRIF.tsv.gz',
                      sep = '\t',
                      usecols = ['name','PMID']).set_index('PMID')

drugrif_counts = dict(Counter(drugrif['name']))

print("init similarities")

get_s3_file("drugrif_cooccur")
get_s3_file("L1000_coexpression")

@app.route('/'+base_name+'/')
def index():
    return render_template('index.html')

@app.route('/'+base_name)
def redirect_index():
    return redirect('/'+base_name+'/')

@app.route('/'+base_name+'/<path:template>')
def send_template(template):
    return render_template(template)

@app.route('/'+base_name+'/api/search', methods=["POST", "GET"])
def search():
    if request.method == 'GET':
        input_json = {"term": request.args.get("term")}
    else:
        input_json = request.get_json()

    searchterm = input_json["term"]

    stime = time.time()

    if searchterm not in session:
        query_geo(searchterm, session)

    associated_drug_counts = drugrif.loc[set(drugrif.index).intersection(set(session[searchterm]))]

    drug_counts = dict(Counter(associated_drug_counts.iloc[:,0]))
    drug_count = {}
    return_size = 0
    for (key, value) in drug_counts.items():
        if value > len(drug_counts)/200 or value/drugrif_counts[key] > 0.07:
            return_size = return_size+1
            drug_count[str(key)] = [value, value/drugrif_counts[key]]

    response = {'search_term': searchterm,
                'PubMedID_count': len(session[searchterm]),
                'drug_count': drug_count,
                'return_size': return_size,
                'query_time': time.time()-stime
                }
    return jsonify(response)

@app.route('/'+base_name+'/api/associate', methods=["POST", "GET"])
def associate():
    if request.method == 'GET':
        input_json = {"drug_list": request.args.get("drug_list").split(","),
                      "similarity": request.args.get("similarity")}
    else:
        input_json = request.get_json()
    
    drugs = input_json["drug_list"]
    similarity = input_json["similarity"]
    
    stime = time.time()

    association = associate_drugs(similarity, drugs, drugrif_counts)

    response = {'association': association, 
        'query_time': time.time()-stime
    }

    return jsonify(response)

@app.route('/'+base_name+'/api/drugpublicationcount', methods=["POST", "GET"])
def drugpublicationcount():
    if request.method == 'GET':
        input_json = {"drugs": request.args.get("drugs")}
    else:
        input_json = request.get_json()
    
    drugs = input_json["drugs"]

    drugcounts = []
    for drug in drugs:
        if drug in drugrif_counts:
            drugcounts.append({"drug": drug, "publications": drugrif_counts[drug]})

    response = {"drugcount": drugcounts}
    return jsonify(response)

@app.route('/'+'/api/drugpublications', methods = ["POST","GET"])
def drugpublications():
    if request.method == 'GET':
        input_json = {"drug": request.args.get("drug"), "term": request.args.get("term")}
    else:
        input_json = request.get_json()
    
    drug = input_json["drug"]
    search_term = input_json["term"]

    if search_term not in session:
        query_geo(search_term, session)

    pmids = session[search_term]
    
    try:
        drugrif_filtered = drugrif[drugrif['name'] == drug]

        # Note: the drugrif dataframe index is PMIDs
        drug_pmids = drugrif_filtered.index.tolist()
        drug_term_pmids = drugrif_filtered[drugrif_filtered.index.isin(pmids)].index.tolist()
        
        response = {"drug_pmids": drug_pmids,
                    "drug_term_pmids": drug_term_pmids,
                    "search_term": search_term,
                    "drug_pmids_count": len(drug_pmids),
                    "drug_term_pmids_count": len(drug_term_pmids_count)}

    except Exception:
        print("drug not found")
    
    return jsonify(response)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)