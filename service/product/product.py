import json
import os
import uuid

from botocore.exceptions import ClientError

from service.product.db_client import DynamoDBClient


def lambda_handler(event, context):
    print(f"request: {event}")

    # TODO : swith case event["httpMethod"] to perform CRUD operations with using DynamoDB Client

    match event["httpMethod"]:
        case "GET":
            if event["path"] is not None:
                body = get_product(event["pathParameters"]["id"])
            else:
                body = get_all_products()

        case "POST":
            body = create_product(event["body"])
        case "PUT":
            # TODO : update product
            pass
        case "DELETE":
            body = delete_product(event["pathParameters"]["id"])

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": body,
    }


def get_product(product_id):
    try:
        dynamodb_client = DynamoDBClient().get_client()

        if not product_id:
            return {
                "statusCode": 400,
                "body": json.dumps(
                    {"error": "Se requiere el ID del producto en la ruta"}
                ),
            }

        try:
            response = dynamodb_client.get_item(Key={"product_id": product_id})
            if "Item" in response:
                return {
                    "statusCode": 200,
                    "body": json.dumps(response["Item"], default=str),
                }
            else:
                return {
                    "statusCode": 404,
                    "body": json.dumps(
                        {"message": f"Producto con ID {product_id} no encontrado"}
                    ),
                }
        except ClientError as e:
            return {
                "statusCode": 500,
                "body": json.dumps(
                    {"error": f"Error al obtener el producto: {str(e)}"}
                ),
            }

    except Exception as e:
        print(e)
        return None


def get_all_products():
    print("get_all_products")
    try:
        dynamodb_client = DynamoDBClient().get_client()

        try:
            response = dynamodb_client.scan()
            items = response.get("Items", [])
            print(f"items: {items}")
            return {
                "statusCode": 200,
                "body": json.dumps(items, default=str),
            }
        except ClientError as e:
            return {
                "statusCode": 500,
                "body": json.dumps(
                    {"error": f"Error al obtener los productos: {str(e)}"}
                ),
            }

    except Exception as e:
        print(e)
        return None


def create_product(product):
    print("create_product")
    print(f"producto recibido: {product}")
    try:
        dynamodb_client = DynamoDBClient().get_client()

        if not product:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Se requiere el producto en el cuerpo"}),
            }

        # Generar un UUID y agregarlo al producto
        product["id"] = {"S": str(uuid.uuid4())}
        print(f"producto con UUID: {product}")

        try:
            response = dynamodb_client.put_item(Item=product)
            print(f"response: {response}")

            return {
                "statusCode": 201,
                "body": json.dumps({"message": "Producto creado exitosamente"}),
            }
        except ClientError as e:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": f"Error al crear el producto: {str(e)}"}),
            }

    except Exception as e:
        print(e)
        return None


def delete_product(product_id):
    print("delete_product")
    try:
        dynamodb_client = DynamoDBClient().get_client()

        if not product_id:
            return {
                "statusCode": 400,
                "body": json.dumps(
                    {"error": "Se requiere el ID del producto en la ruta"}
                ),
            }

        try:
            response = dynamodb_client.delete_item(Key={"product_id": product_id})
            print(f"response: {response}")

            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Producto eliminado exitosamente"}),
            }
        except ClientError as e:
            return {
                "statusCode": 500,
                "body": json.dumps(
                    {"error": f"Error al eliminar el producto: {str(e)}"}
                ),
            }

    except Exception as e:
        print(e)
        return None
