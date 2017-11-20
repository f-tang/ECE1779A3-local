import boto3
from boto3.dynamodb.conditions import Key
from app import get_dbresource

import datetime

if __name__ == '__main__':
    dynamodb = get_dbresource()
    usertable = dynamodb.Table('users')

    response = usertable.query(
        IndexName='UIDIndex',
        KeyConditionExpression=Key('UserID').eq('tester01')
    )
    print(response)

    response = usertable.query(
        IndexName='UIDIndex',
        KeyConditionExpression=Key('UserID').eq('tester02')
    )
    print(response)

    print(str(datetime.datetime.now())[:16])