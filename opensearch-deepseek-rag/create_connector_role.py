# Copyright opensearch-examples contributors
# SPDX-License-Identifier: Apache-2.0


import boto3
import json
import os


create_connector_policy_name = 'create_deepseek_connector_policy'
create_connector_role_name = 'create_deepseek_connector_role'

invoke_connector_role_arn = os.environ['INVOKE_DEEPSEEK_ROLE']
opensearch_service_domain_arn = os.environ['OPENSEARCH_SERVICE_DOMAIN_ARN']


policy = {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "iam:PassRole",
      "Resource": invoke_connector_role_arn
    },
    {
      "Effect": "Allow",
      "Action": "es:ESHttpPost",
      "Resource": opensearch_service_domain_arn
    }
  ]
}


current_user_arn = boto3.resource('iam').CurrentUser().arn
trust_relationship = {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": current_user_arn
      },
      "Action": "sts:AssumeRole"
    }
  ]
}


iam = boto3.client('iam')
sts = boto3.client('sts')


existing_policy = None
try:
  account_id = sts.get_caller_identity()['Account']
  policy_arn = f'arn:aws:iam::{account_id}:policy/{create_connector_policy_name}'
  existing_policy = iam.get_policy(PolicyArn=policy_arn)['Policy']
except iam.exceptions.NoSuchEntityException:
  pass

if existing_policy:
  raise Exception(f"Policy {create_connector_policy_name} already exists. Please set another policy name")


try:
  existing_role = iam.get_role(RoleName=create_connector_role_name)
except iam.exceptions.NoSuchEntityException:
  existing_role = None

if existing_role:
  raise Exception(f"Role {create_connector_role_name} already exists. Please set another role name")


policy = iam.create_policy(
  PolicyName=create_connector_policy_name,
  PolicyDocument=json.dumps(policy)
)
policy_arn = policy['Policy']['Arn']


role = iam.create_role(
  RoleName=create_connector_role_name,
  AssumeRolePolicyDocument=json.dumps(trust_relationship)
)
role_arn = role['Role']['Arn']
iam.attach_role_policy(
  RoleName=create_connector_role_name,
  PolicyArn=policy_arn
)

print(f'Created policy {policy_arn}')
print(f'Created role {role_arn}')

print(f'\nPlease execute the following command\nexport CREATE_DEEPSEEK_CONNECTOR_ROLE="{role_arn}"\n')
