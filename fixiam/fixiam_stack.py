import boto3
import sys

from aws_cdk import (
    Duration,
    RemovalPolicy,
    Stack,
    aws_accessanalyzer as _accessanalyzer,
    aws_events as _events,
    aws_events_targets as _targets,
    aws_iam as _iam,
    aws_lambda as _lambda,
    aws_logs as _logs,
    aws_logs_destinations as _destinations,
    aws_sns as _sns,
    aws_sns_subscriptions as _subs
)

from constructs import Construct

class FixiamStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        account = Stack.of(self).account
        region = Stack.of(self).region

### SNS TOPIC ###

        try:
            client = boto3.client('account')
            operations = client.get_alternate_contact(
                AlternateContactType='OPERATIONS'
            )
            security = client.get_alternate_contact(
                AlternateContactType='SECURITY'
            )
        except:
            print('Missing IAM Permission --> account:GetAlternateContact')
            sys.exit(1)
            pass

        operationstopic = _sns.Topic(
            self, 'operationstopic'
        )

        operationstopic.add_subscription(
            _subs.EmailSubscription(operations['AlternateContact']['EmailAddress'])
        )

        securitytopic = _sns.Topic(
            self, 'securitytopic'
        )

        securitytopic.add_subscription(
            _subs.EmailSubscription(security['AlternateContact']['EmailAddress'])
        )

### LAMBDA LAYER ###

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

        awsaccount = _accessanalyzer.CfnAnalyzer(
            self, 'awsaccount',
            type = 'ACCOUNT',
            analyzer_name = 'awsaccount'
        )

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

        role.add_to_policy(
            _iam.PolicyStatement(
                actions = [
                    'access-analyzer:ListFindings'
                ],
                resources = ['*']
            )
        )

        role.add_to_policy(
            _iam.PolicyStatement(
                actions = [
                    'sns:Publish'
                ],
                resources = [
                    operationstopic.topic_arn,
                    securitytopic.topic_arn
                ]
            )
        )

### ERROR LAMBDA ###

        error = _lambda.Function(
            self, 'error',
            runtime = _lambda.Runtime.PYTHON_3_9,
            code = _lambda.Code.from_asset('error'),
            handler = 'error.handler',
            role = role,
            environment = dict(
                SNS_TOPIC = operationstopic.topic_arn
            ),
            architecture = _lambda.Architecture.ARM_64,
            timeout = Duration.seconds(7),
            memory_size = 128
        )

        errorlogs = _logs.LogGroup(
            self, 'errorlogs',
            log_group_name = '/aws/lambda/'+error.function_name,
            retention = _logs.RetentionDays.ONE_DAY,
            removal_policy = RemovalPolicy.DESTROY
        )

### ALERT LAMBDA ###

        alert = _lambda.Function(
            self, 'alert',
            code = _lambda.Code.from_asset('alert'),
            architecture = _lambda.Architecture.ARM_64,
            runtime = _lambda.Runtime.PYTHON_3_9,
            timeout = Duration.seconds(900),
            handler = 'alert.handler',
            environment = dict(
                ACCOUNT = account,
                REGION = region,
                SNS_TOPIC = securitytopic.topic_arn
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

        errorsub = _logs.SubscriptionFilter(
            self, 'errorsub',
            log_group = logs,
            destination = _destinations.LambdaDestination(error),
            filter_pattern = _logs.FilterPattern.all_terms('ERROR')
        )

        timesub = _logs.SubscriptionFilter(
            self, 'timesub',
            log_group = logs,
            destination = _destinations.LambdaDestination(error),
            filter_pattern = _logs.FilterPattern.all_terms('Task','timed','out')
        )

        alertevent = _events.Rule(
            self, 'alertevent',
            schedule = _events.Schedule.cron(
                minute = '0',
                hour = '0',
                month = '*',
                week_day = '*',
                year = '*'
            )
        )

        alertevent.add_target(
            _targets.LambdaFunction(alert)
        )
