import os

from aws_cdk import RemovalPolicy, Stack
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
            handler="index.handler",
            code=lambda_.Code.from_asset(
                os.path.join(os.path.dirname(__file__), "lambda-handler")
            ),
        )
