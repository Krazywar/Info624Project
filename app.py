import json
import requests
from flask import Flask, render_template,  request, redirect, url_for
from elasticsearch import Elasticsearch
from dataclasses import dataclass

app = Flask(__name__)
cloud_id = "https://info624project.es.us-central1.gcp.cloud.es.io:9243/"
user = "elastic"
api_key = 'search-bcz4qrvbu6v1xrbzxigm4pky'
password = "E8ESWK45BvcnmYFrCmF7MNdW"

es = Elasticsearch(
    hosts=cloud_id,
    basic_auth=(user, password)
)
results = []
engine_name = "info-skiingweather"
es_index = "enterprise-search-engine-info-skiingweather"
states = ['','AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']
formatted_docs = []

@app.route("/")
def index():
    elastiSearchInfo = es.info()
    print(elastiSearchInfo)
    cluster_name = elastiSearchInfo['cluster_name']

    return render_template("index.html", cluster_name=cluster_name)


@app.route('/searchpage', methods=['GET'])
def searchpage():
    if request.method == 'GET':
        app.formatted_docs = []
        # results = es.search(
        #     index=es_index,
        #     body = {
        #     'size' : 10000,
        #     'query': {
        #         'match_all' : {}
        #     }
        # })

        print(results)
        return render_template('searchpage.html', states=states)


@app.route('/searching', methods=["POST"])
def searching():
    print(request.form['ski_query'])
    print(request.form['selected_state'])

    print(request.form['snowfall_slider_min'])
    print(request.form['snowfall_slider_max'])

    #the name of the index
    #enterprise-search-engine-info-skiingweather

    #build the query
    built_query = {
        "query": {
            "bool": {

            }
        }

    }
    built_query["query"]["bool"]["must"] = []

    if request.form['ski_query'] != "":
        built_query["query"]["bool"]["must"].append({"multi_match": {
              "query": request.form['ski_query'],
              "fields": [
                "query",
                "weather_desc",
                "query_type",
                "chance_of_snow",
                "totalsnowfall_cm",
                "windspeed_mph",
                "temp_f"
              ]
            }
        })

    if request.form['selected_state'] != "":
        built_query["query"]["bool"]["must"].append({"match": {"query": request.form['selected_state']}})

    if request.form['snowfall_slider_min'] != "" and request.form['snowfall_slider_max'] != "":
        built_query["query"]["bool"]["must"].append({"range": {"totalsnowfall_cm": {"gte": request.form['snowfall_slider_min'], "lte": request.form['snowfall_slider_max']}}})


    print(built_query)

    result = es.search(
        index=es_index,
        body=built_query
    )

    all_docs = result['hits']['hits']
    print(all_docs)

    #convert the docs to html readable
    # {'_index': '.ent-search-engine-documents-info-skiingweather', '_id': 'doc-622fc597bfd9d5740f933c13',
    #  '_score': 3.1589372,
    #  '_ignored': ['query_type.location', 'totalsnowfall_cm.location', 'totalsnowfall_cm.date', 'weather_desc.float',
    #               'chance_of_snow.date', 'query_type.date', 'query.date', 'weather_desc.date',
    #               'weather_desc.location', 'windspeed_mph.date', 'temp_f.date', 'query.location', 'query.float',
    #               'query_type.float'],
    #  '_source': {'query': 'Kirkwood,CA', 'query_type': 'City', 'weather_desc': 'Clear', 'chance_of_snow': '0',
    #              'totalsnowfall_cm': '0.0', 'temp_f': '36', 'windspeed_mph': '6',
    #              'id': 'doc-622fc597bfd9d5740f933c13'}}


    for doc in all_docs:
        app.formatted_docs.append({
            "Location": doc['_source']['query'],
            "Weather": doc['_source']['weather_desc'],
            "SnowChance": doc['_source']['chance_of_snow'],
            "SnowAmount": doc['_source']['totalsnowfall_cm'],
            "Temp": doc['_source']['temp_f'],
            "Wind": doc['_source']['windspeed_mph'],
            "Score": doc['_score']
        })

    print(formatted_docs)
    return redirect(url_for('results'))


@app.route('/results')
def results():
    return render_template('results.html', docs=app.formatted_docs)




if __name__ == "__main__":
    app.run()
