# Copyright opensearch-examples contributors
# SPDX-License-Identifier: Apache-2.0


import boto3
import json
import os


# This script will create a role and policy document with 
# the following names.
create_connector_policy_name = 'create_deepseek_connector_policy'
create_connector_role_name = 'create_deepseek_connector_role'

# Read environment variables for the invoke role, and the domain ARNs.
invoke_connector_role_arn = os.environ['INVOKE_DEEPSEEK_ROLE']
opensearch_service_domain_arn = os.environ['OPENSEARCH_SERVICE_DOMAIN_ARN']


# This policy will allow post operations on the OpenSearch Service
# domain. It adds a pass role so that OpenSearch can validate the
# connector.
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


# Pulls the current user ARN from Boto's entity resolution, based
# on either aws configure, or environment variables. This role,
# with the policy above enables you to call OpenSearch's
# create_connector API
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


# First validate that the script won't overwrite an existing role or policy. If you receive
# either exception, change the global variable above to give it a different name
#
# Validate that the script won't overwrite an existing policy.  
existing_policy = None
try:
  account_id = sts.get_caller_identity()['Account']
  policy_arn = f'arn:aws:iam::{account_id}:policy/{create_connector_policy_name}'
  existing_policy = iam.get_policy(PolicyArn=policy_arn)['Policy']
  if existing_policy:
    raise Exception(f"Policy {create_connector_policy_name} already exists. Please set another policy name")
except iam.exceptions.NoSuchEntityException:
  # The policy document does not exist. That's the expected result, so there's
  # nothing additional to do
  pass


# Validate that the script won't overwrite an existing role.
existing_role = None
try:
  existing_role = iam.get_role(RoleName=create_connector_role_name)
  if existing_role:
    raise Exception(f"Role {create_connector_role_name} already exists. Please set another role name")
except iam.exceptions.NoSuchEntityException:
  # The role does not exist. That's the expected result, so there's
  # nothing additional to do
  pass  


# Create the policy and role. Note, in actual usage, you should wrap these calls
# in try/except blocks and validate the responses. 
#
# Create the policy
policy = iam.create_policy(
  PolicyName=create_connector_policy_name,
  PolicyDocument=json.dumps(policy)
)
policy_arn = policy['Policy']['Arn']


# Create the role
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
