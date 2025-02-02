# Introduction

This folder uses OpenSearch's connector framework to connect to a DeepSeek R1 model that you host on Amazon SageMaker. Its seven scripts walk you through the code you need to implement retrieval-augmented generation with OpenSearch's `retrieval_augmented_generation` processor.

## Prerequisites

- **Git**: clone the repo https://github.com/Jon-AtAWS/opensearch-examples.git
- **Python**: the code has been tested with Python version 3.13
- **An AWS account**: You’ll need to be able to create an Amazon OpenSearch Service domain, and two Amazon SageMaker endpoints
- **An Integrated Development Environment**: An IDE like Visual Studio Code is helpful, although it’s not strictly necessary
- **AWS command line tools**: Make sure to configure the aws command-line interface with the account you plan to use. Alternately, you can follow the Boto 3 documentation to ensure you use the right credentials.
- **DeepSeek on Amazon SageMaker**: Follow the instructions to [deploy DeepSeek on Amazon SageMaker](https://community.aws/content/2sG84dNUCFzA9z4HdfqTI0tcvKP/deploying-deepseek-r1-on-amazon-sagemaker)
- **An Amazon OpenSearch Service managed clusters domain**: Follow the documentation to [create an Amazon OpenSearch Service domain](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/gsgcreate-domain.html)

## Create your environment

```
cd <root>/opensearch-examples/opensearch-deepseek-rag
python -m venv .venv 
source .venv/bin/activate 
pip install -r requirements.txt 
```

These scripts use environment variables to communicate values. This helps clarify the examples, but is not best practice coding technique. In actual use, you would pass these values as parameters between classes and methods. Set up your environment with the following values.

```
export DEEPSEEK_AWS_REGION='<your current region>' 
export SAGEMAKER_MODEL_INFERENCE_ARN='<your SageMaker endpoint’s ARN>' 
export SAGEMAKER_MODEL_INFERENCE_ENDPOINT='<your SageMaker endpoint’s URL>' 
export OPENSEARCH_SERVICE_DOMAIN_ARN='<your domain’s ARN> 
export OPENSEARCH_SERVICE_DOMAIN_ENDPOINT='<your domain’s API endpoint>' 
export OPENSEARCH_SERVICE_ADMIN_USER='<your domain’s master user name>' 
export OPENSEARCH_SERVICE_ADMIN_PASSWORD='<your domain’s master user password>'
```

# Create IAM roles

Examine and execute the code in `create_invoke_role.py`. Be sure to execute the command in the script's output to set the `INVOKE_DEEPSEEK_ROLE` environment variable. 

Examine and execute the code in `create_connector_role.py`. Be sure to execute the command in the script's output to set the `CREATE_DEEPSEEK_CONNECTOR_ROLE` environment variable.

These two scripts create two roles: one that allows OpenSearch Service to call SageMaker, and one that allows you to call OpenSearch to create a connector.

# Set up OpenSearch's fine-grained access control

Examine and execute the code in `setup_opensearch_security.py`. This code maps the roles that you created onto the `ml_full_access` OpenSearch role to enable you, and subsequent scripts to create the connector, and to call out to SageMaker.

# Create the connector to SageMaker

Examine and execute the code in `create_connector.py`. Be sure to execute the command in the script's output to set the `DEEPSEEK_CONNECTOR_ID` environment variable. You now have a connector that can call SageMaker and invoke DeepSeek to generate text.

# Create an OpenSearch model

Examine and execute the code in `create_deepseek_model.py`. Be sure to execute the command in the script's output to set the `DEEPSEEK_MODEL_ID` environment variable. You now have an OpenSearch model that you can use in Neural queries, ingest pipelines, and search pipelines.

# Deploy an embedding generation model

In the Amazon OpenSearch Service console, open the left navigation menu, scroll down, and select **Integrations**. Select **Configure domain** in the **Integration with text embedding models through Amazon SageMaker** card. Follow the instructions in the AWS CloudFormation template to deploy the `all-MiniLM-L6-v2` model in SageMaker. Once the CloudFormation template has completed, go to the Outputs tab, and copy the `ModelId`, Execute this command to add the model ID to the environment.

```
export EMBEDDING_MODEL_ID='<the model ID from CloudFormation’s output>'
```

# Load the knowledge base

Examine and execute the code in `load_data.py`. This code uses an OpenSearch ingest pipeline to create embeddings for each of the data points. It builds the `population_data` index to serve as a knowledge base for the RAG retrieval.

# Run RAG

Examine and execute the code in `run_rag.py`. This code asks the question "What's the population increase of New York City from 2021 to 2023? How is the trending comparing with Miami?". It uses a `retrieval_augmented_generation` search processor to 1. use a k-NN query to search for relevant results in the knowledge base and 2. send a prompt to DeepSeek R1, augmented with the retrieved information.

Looking at the output, you can see that OpenSearch Service finds New York City, and Miami as `hits` in the retrieval phase. The `answer` includes the prompt, each of the search results, and generated text 

```
{'took': 1, 'timed_out': False, '_shards': {'total': 1, 'successful': 1, 'skipped': 0, 'failed': 0
  }, 'hits': {'total': {'value': 5, 'relation': 'eq'
    }, 'max_score': 0.6477706, 'hits': [
      {'_index': 'population_data', '_id': '4', '_score': 0.6477706, '_source': {'text': 'Chart and table of population level and growth rate for the Miami metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\\nThe current metro area population of Miami in 2023 is 6,
          265,
          000, a 0.8% increase from 2022.\\nThe metro area population of Miami in 2022 was 6,
          215,
          000, a 0.78% increase from 2021.\\nThe metro area population of Miami in 2021 was 6,
          167,
          000, a 0.74% increase from 2020.\\nThe metro area population of Miami in 2020 was 6,
          122,
          000, a 0.71% increase from 2019.'
        }
      },
      {'_index': 'population_data', '_id': '2', '_score': 0.62412775, '_source': {'text': 'Chart and table of population level and growth rate for the New York City metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\\nThe current metro area population of New York City in 2023 is 18,
          937,
          000, a 0.37% increase from 2022.\\nThe metro area population of New York City in 2022 was 18,
          867,
          000, a 0.23% increase from 2021.\\nThe metro area population of New York City in 2021 was 18,
          823,
          000, a 0.1% increase from 2020.\\nThe metro area population of New York City in 2020 was 18,
          804,
          000, a 0.01% decline from 2019.'
        }
      }
    ]
  },
  'ext': {'retrieval_augmented_generation': 
  {'answer': """You are a helpful assistant.\\nGenerate a concise and informative answer in less than 100 words for the given question
  SEARCH RESULT 1: Chart and table of population level and growth rate for the Miami metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\\nThe current metro area population of Miami in 2023 is 6,265,000, a 0.8% increase from 2022.\\nThe metro area population of Miami in 2022 was 6,215,000, a 0.78% increase from 2021.\\nThe metro area population of Miami in 2021 was 6,167,000, a 0.74% increase from 2020.\\nThe metro area population of Miami in 2020 was 6,122,000, a 0.71% increase from 2019.
  SEARCH RESULT 2: Chart and table of population level and growth rate for the New York City metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\\nThe current metro area population of New York City in 2023 is 18,937,000, a 0.37% increase from 2022.\\nThe metro area population of New York City in 2022 was 18,867,000, a 0.23% increase from 2021.\\nThe metro area population of New York City in 2021 was 18,823,000, a 0.1% increase from 2020.\\nThe metro area population of New York City in 2020 was 18,804,000, a 0.01% decline from 2019.
  QUESTION: What's the population increase of New York City from 2021 to 2023? How is the trending comparing with Miami?\\nOkay, so I need to figure out the population increase of New York City from 2021 to 2023 and compare it with Miami's growth. Let me start by looking at the data provided in the search results.\n\nFrom SEARCH RESULT 2, I see that in 2021, NYC had a population of 18,823,000. In 2022, it was 18,867,000, and in 2023, it's 18,937,000. So, the increase from 2021 to 2022 is 18,867,000 - 18,823,000 = 44,000. Then from 2022 to 2023, it's 18,937,000 - 18,867,000 = 70,000. Adding those together, the total increase from 2021 to 2023 is 44,000 + 70,000 = 114,000.\n\nNow, looking at Miami's data in SEARCH RESULT 1. In 2021, Miami's population was 6,167,000, in 2022 it was 6,215,000, and in 2023 it's 6,265,000. The increase from 2021 to 2022 is 6,215,000 - 6,167,000 = 48,000. From 2022 to 2023, it's 6,265,000 - 6,215,000 = 50,000. So, the total increase is 48,000 + 50,000 = 98,000.\n\n
  Comparing the two, NYC's increase of 114,000 is higher than Miami's 98,000. So, NYC's population increased more over that period.\n\nWait, but I should check the growth rates as"
    }
  }
  ```

# Clean up

To avoid incurring charges, clean up the resources you deployed.

* Delete the SageMaker deployment of DeepSeek
* Delete the CloudFormation template for connecting to SageMaker for the embedding model
* Delete the Amazon OpenSearch Service domain




