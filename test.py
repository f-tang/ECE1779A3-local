import boto3
from pymysql import escape_string
from boto3.dynamodb.conditions import Key
from app import get_dbresource, classes

import datetime
import operator

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

    cover_url = "https://s3.amazonaws.com/ece1779-ft/cover_pics/"
    articles = []
    for item in response['Items']:
        r = usertable.query(
            IndexName='UIDIndex',
            KeyConditionExpression=Key('UserID').eq(item['StarterID'])
        )
        if r['Count'] == 0:
            raise ValueError('Cannot find the author.')

        starter_name = r['Items'][0]['Nickname']

        article = classes.article(
            article_id=item['ArticleID'],
            title=item['Title'],
            cover_pic=escape_string(cover_url + item['Tag']),
            tag=item['Tag'],
            starter_id=item['StarterID'],
            starter_name=starter_name,
            create_time=item['CreateTime'],
            modify_time=item['ModifyTime'],
            thumb_num=item['ThumbNum']
        )
        articles.append(article)

    articles.sort(key=operator.attrgetter('modify_time'), reverse=True)
    print(articles)
    articles.sort(key=operator.attrgetter('modify_time'), reverse=False)
    print(articles)

    response = chapter_table.scan()
    print(response)

    print(str(datetime.datetime.now())[:19])