# Copyright opensearch-examples contributors
# SPDX-License-Identifier: Apache-2.0


import boto3
from opensearchpy import OpenSearch
import os


# Read the configuration from environment variables.
opensearch_service_api_endpoint = os.environ['OPENSEARCH_SERVICE_DOMAIN_ENDPOINT']
opensearch_user_name = os.environ['OPENSEARCH_SERVICE_ADMIN_USER']
opensearch_user_password = os.environ['OPENSEARCH_SERVICE_ADMIN_PASSWORD']
create_deepseek_connector_role = os.environ['CREATE_DEEPSEEK_CONNECTOR_ROLE']
lambda_invoke_ml_commons_role_name = 'LambdaInvokeOpenSearchMLCommonsRole'
opensearch_port = 443


if opensearch_service_api_endpoint.startswith('https://'):
  opensearch_service_api_endpoint = opensearch_service_api_endpoint[len('https://'):]
if opensearch_service_api_endpoint.endswith('/'):
  opensearch_service_api_endpoint = opensearch_service_api_endpoint[:-1]


# Construct the backend roles. OpenSearch's fine-grained access control will detect
# signed traffic and map these entities to the ml_full_access role.
sts = boto3.client('sts')
account_id = sts.get_caller_identity()['Account']
lambda_invoke_ml_commons_role_arn = f'arn:aws:iam::{account_id}:role/{lambda_invoke_ml_commons_role_name}'
role_mapping = {
  "backend_roles": [create_deepseek_connector_role,
                    lambda_invoke_ml_commons_role_arn]
}

hosts = [{"host": opensearch_service_api_endpoint, "port": opensearch_port}]
client = OpenSearch(
    hosts=hosts,
    http_auth=(opensearch_user_name, opensearch_user_password),
    use_ssl=True,
    verify_certs=False,
    ssl_assert_hostname=False,
    ssl_show_warn=False,
)
client.security.create_role_mapping('ml_full_access', body=role_mapping)

print(f'ml_full_access role mapping is now {client.security.get_role_mapping("ml_full_access")}')

