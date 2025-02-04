# Copyright opensearch-examples contributors
# SPDX-License-Identifier: Apache-2.0
'''
Loads a data set into OpenSearch Service to serve as a knowledge base for
RAG retrieval. This code uses the OpenSearch Python client, provided by  
opensearch-py, to call OpenSearch's _bulk API with the data. 

It creates embeddings for the documents to support semantic search for
the retrieval via an ingest pipeline. 
'''

from opensearchpy import OpenSearch
import os


opensearch_port = 443
opensearch_service_api_endpoint = os.environ['OPENSEARCH_SERVICE_DOMAIN_ENDPOINT']
opensearch_user_name = os.environ['OPENSEARCH_SERVICE_ADMIN_USER']
opensearch_user_password = os.environ['OPENSEARCH_SERVICE_ADMIN_PASSWORD']
embedding_model_id = os.environ['EMBEDDING_MODEL_ID']
index_name = "population_data"


# Ensure the endpoint matches the contract for the opensearch-py client. Endpoints
# are specified without the leading URL scheme or trailing slashes.
if opensearch_service_api_endpoint.startswith('https://'):
  opensearch_service_api_endpoint = opensearch_service_api_endpoint[len('https://'):]
if opensearch_service_api_endpoint.endswith('/'):
  opensearch_service_api_endpoint = opensearch_service_api_endpoint[:-1]


# The mapping sets kNN to true to enable vector search for the index. It defines
# the text field as type text, and a text_embedding field that uses the FAISS engine
# for storage and retrieval, using the HNSW algorithm.
mapping = {
    "settings": {
        "index": {
            "knn": True,
            "number_of_shards": 1,
            "number_of_replicas": 2
        }
    },
    "mappings": {
        "properties": {
            "text": {"type": "text"},
            "text_embedding": {
              "type": "knn_vector",
              "dimension": 384,
              "method": {
                  "name": "hnsw",
                  "space_type": "l2",
                  "engine": "faiss",
                  "parameters": {"ef_construction": 128, "m": 24},
              }
            }
        }
    }
}


# The data for the knowledge base.
population_data = [
  {"index": {"_index": index_name, "_id": "1"}},
  {"text": "Chart and table of population level and growth rate for the Ogden-Layton metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\nThe current metro area population of Ogden-Layton in 2023 is 750,000, a 1.63% increase from 2022.\nThe metro area population of Ogden-Layton in 2022 was 738,000, a 1.79% increase from 2021.\nThe metro area population of Ogden-Layton in 2021 was 725,000, a 1.97% increase from 2020.\nThe metro area population of Ogden-Layton in 2020 was 711,000, a 2.16% increase from 2019."},
  {"index": {"_index": index_name, "_id": "2"}},
  {"text": "Chart and table of population level and growth rate for the New York City metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\\nThe current metro area population of New York City in 2023 is 18,937,000, a 0.37% increase from 2022.\\nThe metro area population of New York City in 2022 was 18,867,000, a 0.23% increase from 2021.\\nThe metro area population of New York City in 2021 was 18,823,000, a 0.1% increase from 2020.\\nThe metro area population of New York City in 2020 was 18,804,000, a 0.01% decline from 2019."},
  {"index": {"_index": index_name, "_id": "3"}},
  {"text": "Chart and table of population level and growth rate for the Chicago metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\\nThe current metro area population of Chicago in 2023 is 8,937,000, a 0.4% increase from 2022.\\nThe metro area population of Chicago in 2022 was 8,901,000, a 0.27% increase from 2021.\\nThe metro area population of Chicago in 2021 was 8,877,000, a 0.14% increase from 2020.\\nThe metro area population of Chicago in 2020 was 8,865,000, a 0.03% increase from 2019."},
  {"index": {"_index": index_name, "_id": "4"}},
  {"text": "Chart and table of population level and growth rate for the Miami metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\\nThe current metro area population of Miami in 2023 is 6,265,000, a 0.8% increase from 2022.\\nThe metro area population of Miami in 2022 was 6,215,000, a 0.78% increase from 2021.\\nThe metro area population of Miami in 2021 was 6,167,000, a 0.74% increase from 2020.\\nThe metro area population of Miami in 2020 was 6,122,000, a 0.71% increase from 2019."},
  {"index": {"_index": index_name, "_id": "5"}},
  {"text": "Chart and table of population level and growth rate for the Austin metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\\nThe current metro area population of Austin in 2023 is 2,228,000, a 2.39% increase from 2022.\\nThe metro area population of Austin in 2022 was 2,176,000, a 2.79% increase from 2021.\\nThe metro area population of Austin in 2021 was 2,117,000, a 3.12% increase from 2020.\\nThe metro area population of Austin in 2020 was 2,053,000, a 3.43% increase from 2019."},
  {"index": {"_index": index_name, "_id": "6"}},
  {"text": "Chart and table of population level and growth rate for the Seattle metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\\nThe current metro area population of Seattle in 2023 is 3,519,000, a 0.86% increase from 2022.\\nThe metro area population of Seattle in 2022 was 3,489,000, a 0.81% increase from 2021.\\nThe metro area population of Seattle in 2021 was 3,461,000, a 0.82% increase from 2020.\\nThe metro area population of Seattle in 2020 was 3,433,000, a 0.79% increase from 2019."},
]


# OpenSearch ingest pipelines let you define processors to apply to your documents at ingest
# time. The text_embedding processor lets you select a source field and a destination field
# for the embedding. At ingest, OpenSearch will call the model, via its model id, to 
# generate the embedding.
ingest_pipeline_definition = {
  "processors": [
    {
      "text_embedding": {
        "model_id": embedding_model_id,
        "field_map": {
            "text": "text_embedding"
        }
      }
    }
  ]
}


# Set up for the client to call OpenSearch Service
hosts = [{"host": opensearch_service_api_endpoint, "port": opensearch_port}]
client = OpenSearch(
    hosts=hosts,
    http_auth=(opensearch_user_name, opensearch_user_password),
    use_ssl=True,
    verify_certs=False,
    ssl_assert_hostname=False,
    ssl_show_warn=False,
)


# Check whether an index already exists with the chosen name. If you receive an 
# exception, change the index name in the global variable above, and be sure 
# also to change the index_name global variable in run_rag.py
if client.indices.exists(index=index_name) == 200:
  raise Exception(f'Index {index_name} already exists. Please choose a different name in load_data.py. Be sure to change the index_name in run_rag.py as well.')

# This code does not validate the response. In actual use, you should wrap this
# block in try/except and validate the response. 
client.indices.create(index=index_name, body=mapping)
r = client.ingest.put_pipeline(id="embedding_pipeline", 
                               body=ingest_pipeline_definition)
client.bulk(index=index_name, 
            body=population_data,
            pipeline="embedding_pipeline", 
            refresh=True)

print(f'Loaded data into {index_name}')