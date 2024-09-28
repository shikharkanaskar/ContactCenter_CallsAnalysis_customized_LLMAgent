class Bedrock_Runtime_Helper:
    def __init__(self, bedrock_runtime_client) -> None:
        self.bedrock_runtime_client = bedrock_runtime_client

    def invoke_model(self, **kwargs):
        return self.bedrock_runtime_client.invoke_model(**kwargs) #Body of the response returned gives a pointer to a streaming boto3 object where the actual data is stored.