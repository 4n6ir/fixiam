from aws_cdk import (
    Stack,
    aws_accessanalyzer as _accessanalyzer
)

from constructs import Construct

class FixiamStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

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
