# Copyright opensearch-examples contributors
# SPDX-License-Identifier: Apache-2.0


import boto3
import json
import os
import requests 
from requests_aws4auth import AWS4Auth

opensearch_service_api_endpoint = os.environ['OPENSEARCH_SERVICE_DOMAIN_ENDPOINT']
region = os.environ['DEEPSEEK_AWS_REGION']
invoke_role_arn = os.environ['INVOKE_DEEPSEEK_ROLE']
create_deepseek_connector_role_arn = os.environ['CREATE_DEEPSEEK_CONNECTOR_ROLE']
sagemaker_endpoint_url = os.environ['SAGEMAKER_MODEL_INFERENCE_ENDPOINT']


credentials = boto3.client('sts').assume_role(
    RoleArn=create_deepseek_connector_role_arn,
    RoleSessionName='create_connector_session'
)['Credentials']
awsauth = AWS4Auth(credentials['AccessKeyId'], 
                   credentials['SecretAccessKey'], 
                   region, 
                   'es', 
                   session_token=credentials['SessionToken'])


path = '/_plugins/_ml/connectors/_create'
url = opensearch_service_api_endpoint + path

payload = {
  "name": "DeepSeek R1 model connector v2",
  "description": "Connector for my Sagemaker DeepSeek model",
  "version": "1.0",
  "protocol": "aws_sigv4",
  "credential": {
    "roleArn": invoke_role_arn
  },
  "parameters": {
    "service_name": "sagemaker",
    "region": "us-west-2",
    "do_sample": True,
    "top_p": 0.9,
    "temperature": 0.7,
    "max_new_tokens": 512
  },
  "actions": [
    {
      "action_type": "PREDICT",
      "method": "POST",
      "url": sagemaker_endpoint_url,
      "headers": {
        "content-type": "application/json"
      },
      "request_body": "{ \"inputs\": \"${parameters.inputs}\", \"parameters\": {\"do_sample\": ${parameters.do_sample}, \"top_p\": ${parameters.top_p}, \"temperature\": ${parameters.temperature}, \"max_new_tokens\": ${parameters.max_new_tokens}} }",
      "post_process_function": "\n      if (params.result == null || params.result.length == 0) {\n        throw new Exception('No response available');\n      }\n      \n      def completion = params.result[0].generated_text;\n      return '{' +\n               '\"name\": \"response\",'+\n               '\"dataAsMap\": {' +\n                  '\"completion\":\"' + escape(completion) + '\"}' +\n             '}';\n    "
    }
  ]
}

headers = {"Content-Type": "application/json"}

r = requests.post(url, auth=awsauth, json=payload, headers=headers)
print(r.text)
connector_id = json.loads(r.text)['connector_id']
print(connector_id)

print(f'\nPlease execute the following command\nexport DEEPSEEK_CONNECTOR_ID="{connector_id}"\n')
