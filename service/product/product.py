import json
import os
import uuid

from botocore.exceptions import ClientError

from service.product.db_client import DynamoDBClient


def lambda_handler(event, context):
    print(f"request: {event}")

    try:

        match event["httpMethod"]:
            case "GET":
                if event["queryStringParameters"] is not None:
                    body = get_product_by_category(
                        event
                    )  # GET product/1234?category=Phone
                elif event["pathParameters"] is not None:
                    body = get_product(
                        event["pathParameters"]["id"]
                    )  # GET product/{id}
                else:
                    body = get_all_products()  # GET product

            case "POST":
                body = create_product(event)  # POST product
            case "DELETE":
                body = delete_product(
                    event["pathParameters"]["id"]
                )  # DELETE product/{id}
            case "PUT":
                body = update_product(event)  # PUT product/{id}
        print(body)
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
            },
            "message": f"Operación finalizada exitosamente: {event['httpMethod']}",
            "body": body,
        }
    except Exception as e:
        print(e)
        return {
            "statusCode": 500,
            "body": json.dumps(
                {"error": f"La operación ejecutada ha fallado: {str(e)}"}
            ),
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


def create_product(event):
    print("create_product")
    print(f"producto recibido: {event}")
    try:
        dynamodb_client = DynamoDBClient().get_client()

        # Obtener el cuerpo de la solicitud
        product_request = event.get("body")
        # Generar un UUID y agregarlo al producto
        product_id = {"S": str(uuid.uuid4())}
        product_request["id"] = product_id
        print(f"producto con UUID: {product_request["id"]}")

        try:
            response = dynamodb_client.put_item(Item=product_request)
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


def update_product(event):
    print("update_product")
    try:
        dynamodb_client = DynamoDBClient().get_client()

        try:
            response = dynamodb_client.update_item(
                Key={"product_id": event["pathParameters"]["id"]},
                UpdateExpression="SET #name = :name, #price = :price",
                ExpressionAttributeNames={"#name": "name", "#price": "price"},
                ExpressionAttributeValues={
                    ":name": event["body"]["name"],
                    ":price": event["body"]["price"],
                },
            )
            print(f"response: {response}")

            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Producto actualizado exitosamente"}),
            }
        except ClientError as e:
            return {
                "statusCode": 500,
                "body": json.dumps(
                    {"error": f"Error al actualizar el producto: {str(e)}"}
                ),
            }

    except Exception as e:
        print(e)
        return None


def get_product_by_category(event):
    print("get_product_by_category")
    try:
        dynamodb_client = DynamoDBClient().get_client()
        product_id = event["pathParameters"]["id"]
        category = event["queryStringParameters"].get("category")

        try:
            response = dynamodb_client.query(
                KeyConditionExpression="id = :product_id",
                ExpressionAttributeValues={
                    ":product_id": product_id,
                    ":category": category,
                },
                FilterExpression="category = :category",
            )
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
                    {"error": f"Error al obtener los productos por categoría: {str(e)}"}
                ),
            }

    except Exception as e:
        print(e)
        return None
