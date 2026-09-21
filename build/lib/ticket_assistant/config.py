import os

from dotenv import load_dotenv

load_dotenv()

AWS_PROFILE = os.environ["AWS_PROFILE"]
AWS_REGION = os.environ["AWS_REGION"]
MODEL_ID = os.environ["BEDROCK_MODEL_ID"]
GUARDRAIL_ID = os.environ["BEDROCK_GUARDRAIL_ID"]
GUARDRAIL_VERSION = os.environ["BEDROCK_GUARDRAIL_VERSION"]
KNOWLEDGE_BASE_ID = os.environ["BEDROCK_KNOWLEDGE_BASE_ID"]
KNOWLEDGE_BASE_TYPE = os.environ["BEDROCK_KB_TYPE"]
