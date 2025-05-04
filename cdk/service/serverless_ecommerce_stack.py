import os

from aws_cdk import RemovalPolicy, Stack
from aws_cdk import aws_apigateway as apigateway
from aws_cdk import aws_dynamodb as dynamodb  # Duration,; aws_sqs as sqs,
from aws_cdk import aws_lambda as lambda_
from constructs import Construct


class ServerlessEcommerceStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        product_table = dynamodb.TableV2(
            self,
            "product",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING,
            ),
            table_name="product",
            removal_policy=RemovalPolicy.DESTROY,
            billing=dynamodb.Billing.on_demand(),
        )

        product_function = lambda_.Function(
            self,
            "productLambdaFunction",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="product.lambda-handler",
            code=lambda_.Code.from_asset(
                os.path.join(os.path.dirname(__file__), "../service")
            ),
            environment={
                "PRIMARY_KEY": "id",
                "DYNAMODB_TABLE_NAME": product_table.table_name,
            },
        )

        product_table.grant_read_write_data(product_function)

        # Product microservices api gateway
        # root name = product

        # product
        # GET /product
        # POST /product

        # Single product with id parameter
        # GET /product/{id}
        # PUT /product/{id}
        # DELETE /product/{id}

        product_rest_api = apigateway.LambdaRestApi(
            self,
            "productApi",
            handler=product_function,
            rest_api_name="Product Service",
            proxy=False,
        )

        products = product_rest_api.root.add_resource("product")
        products.add_method("GET")  # GET /product
        products.add_method("POST")  # POST /product

        product = products.add_resource("{id}")  # product/{id}
        product.add_method("GET")  # GET /product/{id}
        product.add_method("PUT")  # PUT /product/{id}
        product.add_method("DELETE")  # DELETE /product/{id}
