from aws_cdk import (
    Duration,
    RemovalPolicy,
    Stack,
    aws_accessanalyzer as _accessanalyzer,
    aws_iam as _iam,
    aws_lambda as _lambda,
    aws_logs as _logs
)

from constructs import Construct

class FixiamStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        account = Stack.of(self).account
        region = Stack.of(self).region

        if region == 'ap-northeast-1' or region == 'ap-south-1' or region == 'ap-southeast-1' or \
            region == 'ap-southeast-2' or region == 'eu-central-1' or region == 'eu-west-1' or \
            region == 'eu-west-2' or region == 'me-central-1' or region == 'us-east-1' or \
            region == 'us-east-2' or region == 'us-west-2': number = str(1)

        if region == 'af-south-1' or region == 'ap-east-1' or region == 'ap-northeast-2' or \
            region == 'ap-northeast-3' or region == 'ap-southeast-3' or region == 'ca-central-1' or \
            region == 'eu-north-1' or region == 'eu-south-1' or region == 'eu-west-3' or \
            region == 'me-south-1' or region == 'sa-east-1' or region == 'us-west-1': number = str(2)

        layer = _lambda.LayerVersion.from_layer_version_arn(
            self, 'layer',
            layer_version_arn = 'arn:aws:lambda:'+region+':070176467818:layer:getpublicip:'+number
        )

### ACCESS ANALYZER ###

        organization = _accessanalyzer.CfnAnalyzer(
            self, 'organization',
            type = 'ORGANIZATION',
            analyzer_name = 'organization'
        )

        #awsaccount = _accessanalyzer.CfnAnalyzer(
        #    self, 'awsaccount',
        #    type = 'ACCOUNT',
        #    analyzer_name = 'awsaccount'
        #)

### IAM ROLE ###

        role = _iam.Role(
            self, 'role', 
            assumed_by = _iam.ServicePrincipal(
                'lambda.amazonaws.com'
            )
        )

        role.add_managed_policy(
            _iam.ManagedPolicy.from_aws_managed_policy_name(
                'service-role/AWSLambdaBasicExecutionRole'
            )
        )

### ALERT LAMBDA ###

        alert = _lambda.Function(
            self, 'alert',
            code = _lambda.Code.from_asset('alert'),
            architecture = _lambda.Architecture.ARM_64,
            runtime = _lambda.Runtime.PYTHON_3_9,
            timeout = Duration.seconds(60),
            handler = 'alert.handler',
            environment = dict(
                ACCOUNT = account,
                REGION = region
            ),
            memory_size = 256,
            role = role,
            layers = [
                layer
            ]
        )

        logs = _logs.LogGroup(
            self, 'logs',
            log_group_name = '/aws/lambda/'+alert.function_name,
            retention = _logs.RetentionDays.ONE_DAY,
            removal_policy = RemovalPolicy.DESTROY
        )
