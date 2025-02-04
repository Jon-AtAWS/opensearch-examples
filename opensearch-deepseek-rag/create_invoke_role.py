# Copyright opensearch-examples contributors
# SPDX-License-Identifier: Apache-2.0


import boto3
import json
import os

invoke_deepseek_policy_name = 'invoke_deepseek_policy'
invoke_deepseek_role_name = 'invoke_deepseek_role'
sagemaker_model_inference_endpoint_arn = os.environ['SAGEMAKER_MODEL_INFERENCE_ARN']


policy = {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sagemaker:InvokeEndpoint"
      ],
      "Resource": [
        sagemaker_model_inference_endpoint_arn
      ]
    }
  ]
}


trust_relationship = {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "es.amazonaws.com"
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
  policy_arn = f'arn:aws:iam::{account_id}:policy/{invoke_deepseek_policy_name}'
  existing_policy = iam.get_policy(PolicyArn=policy_arn)['Policy']
except iam.exceptions.NoSuchEntityException:
  pass

if existing_policy:
  raise Exception(f"Policy {invoke_deepseek_policy_name} already exists. Please set another policy name")


try:
  existing_role = iam.get_role(RoleName=invoke_deepseek_role_name)
except iam.exceptions.NoSuchEntityException:
  existing_role = None

if existing_role:
  raise Exception(f"Role {invoke_deepseek_role_name} already exists. Please set another role name")


policy = iam.create_policy(
  PolicyName=invoke_deepseek_policy_name,
  PolicyDocument=json.dumps(policy)
)
policy_arn = policy['Policy']['Arn']


role = iam.create_role(
  RoleName=invoke_deepseek_role_name,
  AssumeRolePolicyDocument=json.dumps(trust_relationship)
)
print(role)
role_arn = role['Role']['Arn']
iam.attach_role_policy(
  RoleName=invoke_deepseek_role_name,
  PolicyArn=policy_arn
)

print(f'Created policy {policy_arn}')
print(f'Created role {role_arn}')

print(f'\nPlease execute the following command\nexport INVOKE_DEEPSEEK_ROLE="{role_arn}"\n')