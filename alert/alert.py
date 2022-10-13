import boto3
import json
import os

def handler(event, context):

    account = os.environ['ACCOUNT']
    region = os.environ['REGION']

    accessanalyzer = boto3.client('accessanalyzer')
    sns_client = boto3.client('sns')

    awsaccount = 'arn:aws:access-analyzer:'+region+':'+account+':analyzer/awsaccount'
    
    paginator = accessanalyzer.get_paginator('list_findings')
    
    pages = paginator.paginate(
        analyzerArn = awsaccount
    )
    
    for page in pages:
        for finding in page['findings']:
            try:
                if finding['error'] == 'ACCESS_DENIED' and finding['status'] != 'ARCHIVED':
                    print(finding)
                    response = sns_client.publish(
                        TopicArn = os.environ['SNS_TOPIC'],
                        Subject = 'IAM Access Analyzer Alert',
                        Message = str(finding)
                    )
            except:
                pass
            try:
                if finding['isPublic'] == True and finding['status'] != 'ARCHIVED':
                    print(finding)
                    response = sns_client.publish(
                        TopicArn = os.environ['SNS_TOPIC'],
                        Subject = 'IAM Access Analyzer Alert',
                        Message = str(finding)
                    )
            except:
                pass

    organization = 'arn:aws:access-analyzer:'+region+':'+account+':analyzer/organization'

    paginator = accessanalyzer.get_paginator('list_findings')
    
    pages = paginator.paginate(
        analyzerArn = organization
    )
    
    for page in pages:
        for finding in page['findings']:
            try:
                if finding['error'] == 'ACCESS_DENIED' and finding['status'] != 'ARCHIVED':
                    print(finding)
                    response = sns_client.publish(
                        TopicArn = os.environ['SNS_TOPIC'],
                        Subject = 'IAM Access Analyzer Alert',
                        Message = str(finding)
                    )
            except:
                pass
            try:
                if finding['isPublic'] == True and finding['status'] != 'ARCHIVED':
                    print(finding)
                    response = sns_client.publish(
                        TopicArn = os.environ['SNS_TOPIC'],
                        Subject = 'IAM Access Analyzer Alert',
                        Message = str(finding)
                    )
            except:
                pass

    return {
        'statusCode': 200,
        'body': json.dumps('IAM Access Analyzer Alerts')
    }