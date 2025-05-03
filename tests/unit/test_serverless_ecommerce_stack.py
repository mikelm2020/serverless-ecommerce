import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk.service.serverless_ecommerce_stack import ServerlessEcommerceStack


# example tests. To run these tests, uncomment this file along with the example
# resource in serverless_ecommerce/serverless_ecommerce_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = ServerlessEcommerceStack(app, "serverless-ecommerce")
    template = assertions.Template.from_stack(stack)


#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
