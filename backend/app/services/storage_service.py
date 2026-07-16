import boto3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

DOWNLOAD_FOLDER = BASE_DIR / "data" / "downloads"
DOWNLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


class StorageService:

    def __init__(self):

        self.client = boto3.client(
            "s3",
            endpoint_url="http://localhost:9000",
            aws_access_key_id="admin",
            aws_secret_access_key="password123",
        )

        self.bucket = "documents"

    def download_all(self):

        response = self.client.list_objects_v2(
            Bucket=self.bucket
        )

        files = []

        for obj in response.get("Contents", []):

            filename = obj["Key"]

            destination = DOWNLOAD_FOLDER / filename

            self.client.download_file(
                self.bucket,
                filename,
                str(destination)
            )

            files.append(destination)

        return files