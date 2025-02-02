# Copyright opensearch-examples contributors
# SPDX-License-Identifier: Apache-2.0


import os
import requests
from requests_aws4auth import AWS4Auth

opensearch_service_api_endpoint = os.environ['OPENSEARCH_SERVICE_DOMAIN_ENDPOINT']
opensearch_user_name = os.environ['OPENSEARCH_SERVICE_ADMIN_USER']
opensearch_user_password = os.environ['OPENSEARCH_SERVICE_ADMIN_PASSWORD']
region = os.environ['DEEPSEEK_AWS_REGION']
connector_id = os.environ['DEEPSEEK_CONNECTOR_ID']
create_deepseek_connector_role = os.environ['CREATE_DEEPSEEK_CONNECTOR_ROLE']


userauth = (opensearch_user_name, opensearch_user_password)
headers = {"Content-Type": "application/json"}


########################################################################################
# Create a Model Group for the model
path = '/_plugins/_ml/model_groups/_register'
url = opensearch_service_api_endpoint + path
payload = {
    "name": "Sagemaker DeepSeek model v2",
    "description": "Model group for DeepSeek model"
}
r = requests.post(url, auth=userauth, json=payload, headers=headers)
model_group_id = r.json()[f'model_group_id']
print(f'model_group_id: {model_group_id}')


########################################################################################
# Register the model
path = '/_plugins/_ml/models/_register'
url = opensearch_service_api_endpoint + path
payload = {
  "name": "Sagemaker DeepSeek R1 model",
  "function_name": "remote",
  "description": "DeepSeek R1 model on Sagemaker",
  "model_group_id": model_group_id,
  "connector_id": connector_id
}
r = requests.post(url, auth=userauth, json=payload, headers=headers)

model_id = r.json()['model_id']
print(f'model_id: {model_id}')


########################################################################################
# Deploy the model
path = f'/_plugins/_ml/models/model_id/_deploy'
url = opensearch_service_api_endpoint + path
r = requests.post(url, auth=userauth, headers=headers)


print(f'\nPlease execute the following command\nexport DEEPSEEK_MODEL_ID="{model_id}"\n')
