# Deploy function

# Lambda Trigger
import os
import zipfile
import subprocess
from lambda_configuration import files_lambda, dependencies, zipFileName, function_name, description, runtime, role, handler_name, publish, account_id, region


class Lambda_Helper:
    def __init__(self, lambda_client) -> None:
        self.lambda_client = lambda_client
        self.files_lambda = files_lambda
        self.zipFileName = zipFileName
        self.function_name = function_name
        self.description = description
        self.runtime = runtime
        self.role = role
        self.handler_name = handler_name
        self.publish = publish
        self.create_deployment_package()

    def create_deployment_package(self):
        print("Inside")
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        print(f"Base directory is: {base_dir}")
        with zipfile.ZipFile(zipFileName, 'w') as lambda_zip:
            for file in files_lambda:
                lambda_zip.write(file, os.path.relpath(file))

            print("In between")

            print("Outside")

    def deploy_function(self):
        print("Inside deploy function")
        with open(self.zipFileName, 'rb') as f:
            deployment_package = f.read()

        print("Read")

        response = self.lambda_client.create_function(
            Code = {
                'ZipFile': deployment_package
            },
            Description = description,
            FunctionName = function_name,
            Handler= handler_name,
            Publish = publish,
            Role = role,
            Runtime = runtime,
        )
        print(f"Function {function_name} deployed & response is: {response}")
        return response

    def update_function_code(self):
        try:
            self.create_deployment_package()
            with open(self.zipFileName, 'rb') as f:
                deployment_package = f.read()
            response = self.lambda_client.update_function_code(
                FunctionName=function_name, ZipFile=deployment_package
            )
            print(f"Successfully updated lambda function: {function_name}")
        except Exception as err:
            print(
                "Couldn't update function %s. Here's why: %s: %s",
                function_name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
        else:
            return response

    def add_lambda_trigger(self, bucket_name, s3_client):
        # Adding permission for S3 to invoke the Lambda function
        try:
            self.lambda_client.add_permission(
                FunctionName = function_name,
                StatementId = 'S3InvokeLambdaPermission',
                Action = 'lambda:InvokeFunction',
                Principal = 's3.amazonaws.com',
                SourceArn = f'arn:aws:s3:::{bucket_name}',
                SourceAccount = account_id
            )
        except Exception as e:
            pass

        # Set up the bucket notification to trigger Lambda on .json file creation
        notification_configuration = {
            "LambdaFunctionConfigurations": [
                {
                    "LambdaFunctionArn": f'arn:aws:lambda:{region}:{account_id}:function:{function_name}',
                    "Events": ["s3:ObjectCreated:*"],
                    "Filter": {
                        "Key": {
                            "FilterRules": [
                                {
                                    "Name": "suffix",
                                    "Value": ".json"
                                }
                            ]
                        }
                    }
                }
            ]
        }

        return s3_client.enable_trigger_for_lambda(bucket_name, notification_configuration)


