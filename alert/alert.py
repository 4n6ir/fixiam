import boto3
import json
import os

def handler(event, context):

    account = os.environ['ACCOUNT']
    region = os.environ['REGION']
    analyzer = 'arn:aws:access-analyzer:'+region+':'+account+':analyzer/organization'

    print(analyzer)

    return {
        'statusCode': 200,
        'body': json.dumps('IAM Access Analyzer Alerts')
    }