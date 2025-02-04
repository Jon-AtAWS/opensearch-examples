# Copyright opensearch-examples contributors
# SPDX-License-Identifier: Apache-2.0


import boto3
import json
import os

# The script will create a role and policy with the names below. It
# reads the ARN for the SageMaker endpoint from the environment.
invoke_deepseek_policy_name = 'invoke_deepseek_policy'
invoke_deepseek_role_name = 'invoke_deepseek_role'
sagemaker_model_inference_endpoint = os.environ['SAGEMAKER_MODEL_INFERENCE_ARN']


# Allows invoke endpoint
policy = {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sagemaker:InvokeEndpoint"
      ],
      "Resource": [
        sagemaker_model_inference_endpoint
      ]
    }
  ]
}


# Allows OpenSearch Service to assume the role. The role and policy
# together allow OpenSearch Service to call SageMaker to invoke
# DeepSeek to generate text.
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


# Check for an existing policy with the same name, and error out
# if it exists.
iam = boto3.client('iam')
sts = boto3.client('sts')
existing_policy = None
try:
  # This constructs an ARN for the policy based on the current
  # account. If you need to run this for another account, you can 
  # change the account ID below.
  account_id = sts.get_caller_identity()['Account']
  policy_arn = f'arn:aws:iam::{account_id}:policy/{invoke_deepseek_policy_name}'
  existing_policy = iam.get_policy(PolicyArn=policy_arn)['Policy']
  if existing_policy:
    raise Exception(f"Policy {invoke_deepseek_policy_name} already exists. Please set another policy name")
except iam.exceptions.NoSuchEntityException:
  pass


# Check for an existing policy with the same name, and error out
# if it exists.
existing_role = None
try:
  existing_role = iam.get_role(RoleName=invoke_deepseek_role_name)
  if existing_role:
    raise Exception(f"Role {invoke_deepseek_role_name} already exists. Please set another role name")
except iam.exceptions.NoSuchEntityException:
  pass


# Create the policy
policy = iam.create_policy(
  PolicyName=invoke_deepseek_policy_name,
  PolicyDocument=json.dumps(policy)
)
policy_arn = policy['Policy']['Arn']


# Create the role, with the policy document just created.
role = iam.create_role(
  RoleName=invoke_deepseek_role_name,
  AssumeRolePolicyDocument=json.dumps(trust_relationship)
)
role_arn = role['Role']['Arn']
iam.attach_role_policy(
  RoleName=invoke_deepseek_role_name,
  PolicyArn=policy_arn
)

print(f'Created policy {policy_arn}')
print(f'Created role {role_arn}')

print(f'\nPlease execute the following command\nexport INVOKE_DEEPSEEK_ROLE="{role_arn}"\n')