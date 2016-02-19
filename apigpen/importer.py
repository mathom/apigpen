import boto3


def import_api(name_or_id, data):
    api = boto3.client('apigateway')
