import boto3
import securing_credentials

ACCESS_KEY = securing_credentials.ACCESS_KEY
SECRET_KEY = securing_credentials.SECRET_KEY
LOGGING_ARN = securing_credentials.LOGGING_ARN

bedrock_runtime_client = boto3.client(
    'bedrock-runtime',
    region_name='us-east-1',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
)

bedrock_client = boto3.client(
    'bedrock',
    region_name='us-east-1',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
)

s3_client = boto3.client(
    's3',
    region_name = 'us-east-1',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
)

transcribe_client = boto3.client(
    'transcribe',
    region_name = 'us-east-1',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
) # Transcribe client so we can do inference/generation with our model.

cloudwatch_client = boto3.client(
    'logs',
    region_name='us-east-1',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
)


lambda_client = boto3.client(
    'lambda',
    region_name='us-east-1',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
)