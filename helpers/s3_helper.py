class S3_Helper:
    def __init__(self, s3_client) -> None:
        self.s3_client = s3_client

    def enable_trigger_for_lambda(self, bucket_name, notification_configuration):
        response = self.s3_client.put_bucket_notification_configuration(
            Bucket = bucket_name,
            NotificationConfiguration = notification_configuration
        )
        print(f"Successfully enabled trigger for bucket: {bucket_name} and response is: {response}")
        return response

    def upload_file(self, bucket_name, file_name, object_name=None):
        response = self.s3_client.upload_file(file_name, bucket_name, object_name)
        print(f"Successfully uploaded data from file {file_name} to bucket {bucket_name}")
        return response

    def get_object(self, bucket_name, object_key):
        return self.s3_client.get_object(Bucket=bucket_name, Key = object_key)

