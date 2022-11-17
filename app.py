#!/usr/bin/env python3
import boto3
import os

import aws_cdk as cdk

from fixiam.fixiam_stack import FixiamStack

app = cdk.App()

client = boto3.client('ec2')
regions = client.describe_regions()

for region in regions['Regions']:

    if region['RegionName'] != 'me-central-1' and region['RegionName'] != 'eu-central-2' and region['RegionName'] != 'eu-south-2':

        FixiamStack(
            app, 'FixiamStack-'+region['RegionName'],
            env = cdk.Environment(
                account = os.getenv('CDK_DEFAULT_ACCOUNT'),
                region = region['RegionName']
            ),
            synthesizer = cdk.DefaultStackSynthesizer(
                qualifier = '4n6ir'
            )
        )

cdk.Tags.of(app).add('Alias','ALL')
cdk.Tags.of(app).add('GitHub','https://github.com/4n6ir/fixiam.git')

app.synth()
