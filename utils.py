import pandas as pd
import numpy as np
import h5py as h5
import os
import urllib.request
import re
import requests
from datetime import datetime, timedelta
import concurrent.futures

def get_s3_file(filename):
    if not os.path.exists('similarity'):
        os.makedirs('similarity')
    if filename != 'NA' and not os.path.isfile(f"similarity/{filename}.h5"):
        url = f'https://appyters.maayanlab.cloud/storage/DrugShot/{filename}.h5'
        urllib.request.urlretrieve(url, f'similarity/{filename}.h5')


def query_ncbi(searchterm, api_key, session):
    countMax = 1000000
    pagestep = 1000000
    going = True
    i = 0
    pmids = []
    
    print(searchterm)
    print(api_key)
    print(session)

    while going:

        url = ("https://eutils.ncbi.nlm.nih.gov"+
            "/entrez/eutils/esearch.fcgi"+
            "?db=pubmed&term="+searchterm+
            "&retstart="+str(i*pagestep)+
            "&retmax="+str(pagestep)+
            "&api_key="+api_key)
        
        page = requests.get(url).text
        pmids = pmids + re.findall(r'Id>(.*?)<', page)
        if i==0:
            countMax = int(re.findall(r'Count>(.*?)<', page)[0])
        if i*pagestep > countMax:
            going = False

        i += 1

    session[searchterm] = np.array(pmids).astype(int)

def query_geo(searchterm, api_key, session):
    start_date = datetime(2000, 1, 1)
    end_date = datetime(2022, 1, 1)
    quarter = timedelta(days=365.25 / 4)
    date_list = []
    current_date = start_date
    while current_date < end_date:
        date_list.append(current_date.strftime('%Y/%m/%d'))
        current_date += quarter
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(query_geo_date, searchterm, api_key, date_list[i], date_list[i + 1]) for i in range(len(date_list) - 1)]
        for future in concurrent.futures.as_completed(futures):
            results.extend(future.result())
    
    pmids = list(set(results))
    session[searchterm] = np.array(pmids).astype(int)

def query_geo_date(searchterm, api_key, mindate, maxdate):
    pmids = []
    url = ("https://eutils.ncbi.nlm.nih.gov"+
        "/entrez/eutils/esearch.fcgi"+
        "?db=pubmed&term="+searchterm+
        "&mindate="+str(mindate)+
        "&maxdate="+str(maxdate)+
        "&retmax=10000"+
        "&api_key="+api_key)
    page = requests.get(url).text
    pmids = pmids + re.findall(r'Id>(.*?)<', page)
    return pmids

def slice_matrix(matrix, query_colids):
    f = h5.File(f"similarity/{matrix}.h5", "r")
    query_colids = set([x.upper() for x in query_colids])
    colids = list(f["meta"]["colid"])
    try:
        colids = [x.decode("UTF-8") for x in colids]
    except:
        print("already good")
    col_idx = [i for i, x in enumerate(colids) if x.upper() in query_colids]
    values = pd.DataFrame(f["data"]["matrix"][:, col_idx], columns=np.array(colids)[col_idx], index=colids, dtype=float)
    f.close()
    for g in values.columns:
        values.loc[g,g] = float('NaN')
    return values

def associate_drugs(similarity, drugs, drugcounts):
    matrix_slice = slice_matrix(similarity, drugs)
    mean_score = matrix_slice.mean(axis=1).sort_values(ascending=False)[0:200]
    asso = {}
    for d in mean_score.index:
        if d not in drugs: # don't want drugs from unweighted drug set in predictions
            topDrugs = {}
            topScores = {}
            drugc = 0

            drugc = drugcounts[d] if d in drugcounts else 0
            asso[d] = {"simScore": mean_score[d],
                    "topDrugs": topDrugs,
                    "topScores": topScores,
                    "publications": drugc}

    return (asso)