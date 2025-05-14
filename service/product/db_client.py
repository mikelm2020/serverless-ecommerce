import json
import os

import boto3
from botocore.exceptions import ClientError

# Nombre de la tabla de DynamoDB (configurado como variable de entorno)
DYNAMODB_TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME")


class DynamoDBClient:
    """
    Implementación del patrón Singleton para el cliente de DynamoDB.
    """

    _instance = None
    _client = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DynamoDBClient, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not DynamoDBClient._client:
            DynamoDBClient._client = boto3.resource("dynamodb")
            self.table = DynamoDBClient._client.Table(DYNAMODB_TABLE_NAME)

    def get_client(self):
        return self.table
