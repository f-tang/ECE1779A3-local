import boto3
from boto3.dynamodb.conditions import Key
from app import get_dbresource

import datetime

if __name__ == '__main__':
    dynamodb = get_dbresource()
    usertable = dynamodb.Table('users')
    article_table = dynamodb.Table('articles')
    chapter_table = dynamodb.Table('chapters')
    comment_table = dynamodb.Table('comments')

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

    # article_table.update_item(
    #     Key={
    #         'ArticleID': '1511229514953828'
    #     },
    #     UpdateExpression="set ModifyTime = :m",
    #     ExpressionAttributeValues={
    #         ':m': str(datetime.datetime.now())[:16]
    #     },
    #     ReturnValues = "UPDATED_NEW"
    # )

    response = article_table.scan()
    print(response)

    response = chapter_table.scan()
    print(response)

    print(str(datetime.datetime.now())[:16])