#!/usr/bin/env python3
import os

import aws_cdk as cdk

from fixiam.fixiam_stack import FixiamStack

app = cdk.App()

FixiamStack(
    app, 'FixiamStack',
    env = cdk.Environment(
        account = os.getenv('CDK_DEFAULT_ACCOUNT'),
        region = os.getenv('CDK_DEFAULT_REGION')
    ),
    synthesizer = cdk.DefaultStackSynthesizer(
        qualifier = '4n6ir'
    )
)

cdk.Tags.of(app).add('fixiam','fixiam')


app.synth()
