import boto3
from botocore.exceptions import ClientError


def get_s3_client():
    return boto3.client("s3")


def read_text(bucket: str, key: str) -> str:
    s3 = get_s3_client()
    obj = s3.get_object(Bucket=bucket, Key=key)
    return obj["Body"].read().decode("utf-8")


def write_text(bucket: str, key: str, content: str) -> None:
    s3 = get_s3_client()
    s3.put_object(Bucket=bucket, Key=key, Body=content.encode("utf-8"))


def exists(bucket: str, key: str) -> bool:
    s3 = get_s3_client()
    try:
        s3.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as e:
        if e.response["ResponseMetadata"]["HTTPStatusCode"] == 404:
            return False
        raise
