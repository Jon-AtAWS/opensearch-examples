# Copyright opensearch-examples contributors
# SPDX-License-Identifier: Apache-2.0
'''
This module creates an OpenSearch model 
(see: https://opensearch.org/docs/latest/ml-commons-plugin/api/model-apis/index/)
that you use to connect to SageMaker/DeepSeek. It
uses the requests library with username/password authentication to call OpenSearch's
REST API directly.

As a side effect, OpenSearch automatically creates a model group for the model. Model
groups (see: https://opensearch.org/docs/latest/ml-commons-plugin/api/model-group-apis/index/)
help you control access to your OpenSearch models.
'''


import os
import requests


opensearch_service_api_endpoint = os.environ['OPENSEARCH_SERVICE_DOMAIN_ENDPOINT']
opensearch_user_name = os.environ['OPENSEARCH_SERVICE_ADMIN_USER']
opensearch_user_password = os.environ['OPENSEARCH_SERVICE_ADMIN_PASSWORD']
region = os.environ['DEEPSEEK_AWS_REGION']
connector_id = os.environ['DEEPSEEK_CONNECTOR_ID']
create_deepseek_connector_role = os.environ['CREATE_DEEPSEEK_CONNECTOR_ROLE']


# Set up user/password auth
userauth = (opensearch_user_name, opensearch_user_password)
headers = {"Content-Type": "application/json"}


########################################################################################
# Register the model
path = '/_plugins/_ml/models/_register'
url = opensearch_service_api_endpoint + path
payload = {
  "name": "Sagemaker DeepSeek R1 model",
  "function_name": "remote",
  "description": "DeepSeek R1 model on Sagemaker",
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
