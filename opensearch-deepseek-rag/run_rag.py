# Copyright opensearch-examples contributors
# SPDX-License-Identifier: Apache-2.0


from opensearchpy import OpenSearch
import os


opensearch_port = 443
opensearch_service_api_endpoint = os.environ['OPENSEARCH_SERVICE_DOMAIN_ENDPOINT']
opensearch_user_name = os.environ['OPENSEARCH_SERVICE_ADMIN_USER']
opensearch_user_password = os.environ['OPENSEARCH_SERVICE_ADMIN_PASSWORD']
embedding_model_id = os.environ['EMBEDDING_MODEL_ID']
generation_model_id = os.environ['DEEPSEEK_MODEL_ID']
index_name = "population_data"


if opensearch_service_api_endpoint.startswith('https://'):
  opensearch_service_api_endpoint = opensearch_service_api_endpoint[len('https://'):]
if opensearch_service_api_endpoint.endswith('/'):
  opensearch_service_api_endpoint = opensearch_service_api_endpoint[:-1]


hosts = [{"host": opensearch_service_api_endpoint, "port": opensearch_port}]
client = OpenSearch(
    hosts=hosts,
    http_auth=(opensearch_user_name, opensearch_user_password),
    use_ssl=True,
    verify_certs=False,
    ssl_assert_hostname=False,
    ssl_show_warn=False,
)


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
  "ext": {
    "generative_qa_parameters": {
      "llm_model": "bedrock/claude",
      "llm_question": "What's the population increase of New York City from 2021 to 2023? How is the trending comparing with Miami?",
      "context_size": 5,
      "timeout": 15
    }
  }
}


client.search_pipeline.put(id='deepseek_rag_pipeline',
                           body=search_pipeline_definition)

resp = client.search(body=query, index=index_name, search_pipeline="deepseek_rag_pipeline", timeout=300)
print(resp)