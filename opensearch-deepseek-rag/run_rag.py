# Copyright opensearch-examples contributors
# SPDX-License-Identifier: Apache-2.0
'''
Uses an OpenSearch search processor to perform retrieval augmented generation. First,
define the processor, and send to OpenSearch with the opensearch-py client. Then send 
a query through the pipeline, encapsulating a user question and engaging an langauge
generation model to respond.
'''

from opensearchpy import OpenSearch
import os


opensearch_port = 443
opensearch_service_api_endpoint = os.environ['OPENSEARCH_SERVICE_DOMAIN_ENDPOINT']
opensearch_user_name = os.environ['OPENSEARCH_SERVICE_ADMIN_USER']
opensearch_user_password = os.environ['OPENSEARCH_SERVICE_ADMIN_PASSWORD']
embedding_model_id = os.environ['EMBEDDING_MODEL_ID']
generation_model_id = os.environ['DEEPSEEK_MODEL_ID']
# Note: if you changed the index name in load_data.py, be sure to change it here.
index_name = "population_data"


# Ensure the endpoint matches the contract for the opensearch-py client. Endpoints
# are specified without the leading URL scheme or trailing slashes.
if opensearch_service_api_endpoint.startswith('https://'):
  opensearch_service_api_endpoint = opensearch_service_api_endpoint[len('https://'):]
if opensearch_service_api_endpoint.endswith('/'):
  opensearch_service_api_endpoint = opensearch_service_api_endpoint[:-1]


# Prepare the client with username/password authetication
hosts = [{"host": opensearch_service_api_endpoint, "port": opensearch_port}]
client = OpenSearch(
    hosts=hosts,
    http_auth=(opensearch_user_name, opensearch_user_password),
    use_ssl=True,
    verify_certs=False,
    ssl_assert_hostname=False,
    ssl_show_warn=False,
)


# The search pipeline uses a retrieval_augmented_generation processor to
# send the question and search results for a generated response.
search_pipeline_definition = {
  "response_processors": [
    {
      "retrieval_augmented_generation": {
        "tag": "Demo pipeline",
        "description": "Demo pipeline Using DeepSeek R1",
        "model_id": generation_model_id,
        "context_field_list": [
          "text"
        ],
        "system_prompt": "You are a helpful assistant.",
        "user_instructions": "Generate a concise and informative answer in less than 100 words for the given question"
      }
    }
  ]
}


# The neural query uses the embedding model to generate an embedding for the query_text
# and performs a kNN query to get nearest-neighbor matches. Note we set the size query
# parameter to 2, with k=5. These are very tight constraints that work for this example.
# In actual use, you would set both k and size higher.
query = {
  "query": {
    "neural": {
      "text_embedding": {
        "query_text": "What's the population increase of New York City from 2021 to 2023? How is the trending comparing with Miami?",
        "model_id": embedding_model_id,
        "k": 5
      }
    }
  },
  "size": 2,
  "_source": [
    "text"
  ],
  # In this case, you use the "bedrock/claude" parameterization of the connector
  # template. The connector itself sends the request to the SageMaker endpoint,
  # hosting DeepSeek in the example. Stay tuned for a DeepSeek connector blueprint
  # in the blueprints repository.
  "ext": {
    "generative_qa_parameters": {
      "llm_model": "bedrock/claude",
      "llm_question": "What's the population increase of New York City from 2021 to 2023? How is the trending comparing with Miami?",
      "context_size": 5,
      "timeout": 15
    }
  }
}


# Put the search pipeline, and send the query to it. 
client.search_pipeline.put(id='deepseek_rag_pipeline',
                           body=search_pipeline_definition)
resp = client.search(body=query,
                     index=index_name, 
                     search_pipeline="deepseek_rag_pipeline",
                     timeout=300)
print(resp)