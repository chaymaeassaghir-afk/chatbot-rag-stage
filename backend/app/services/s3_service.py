import boto3
from botocore.client import Config


class S3Service:

    def __init__(self):

        self.client = boto3.client(
            "s3",
            endpoint_url="http://localhost:9000",      # MinIO ou AWS
            aws_access_key_id="ACCESS_KEY",
            aws_secret_access_key="SECRET_KEY",
            config=Config(signature_version="s3v4")
        )

        self.bucket = "documents"

    def list_files(self):

        response = self.client.list_objects_v2(
            Bucket=self.bucket
        )

        if "Contents" not in response:
            return []

        return response["Contents"]

    def download_file(self, key):

        response = self.client.get_object(
            Bucket=self.bucket,
            Key=key
        )

        return response["Body"].read()