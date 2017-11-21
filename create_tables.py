import boto3
from boto3.dynamodb.conditions import Key


dynamodb = boto3.resource('dynamodb', region_name='us-east-1', endpoint_url="http://localhost:8000")
# dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

def create_users():
    dynamodb.create_table(
        TableName='users',

        KeySchema=[
            {
                'AttributeName': 'UserID',
                'KeyType':'HASH'
            },
        ],

        GlobalSecondaryIndexes=[
            {
                'IndexName': 'UIDIndex',
                'KeySchema': [
                    {
                        'AttributeName': 'UserID',
                        'KeyType': 'HASH'
                    }
                ],
                'Projection': {
                    'ProjectionType': 'INCLUDE',
                    'NonKeyAttributes': ['Password', 'Email', 'Nickname']
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 2,
                    'WriteCapacityUnits': 2
                }
            },
            {
                'IndexName': 'NicknameIndex',
                'KeySchema': [
                    {
                        'AttributeName': 'Nickname',
                        'KeyType': 'HASH'
                    }
                ],
                'Projection': {
                    'ProjectionType': 'KEYS_ONLY'
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 2,
                    'WriteCapacityUnits': 2
                }
            }
        ],

        AttributeDefinitions=[
            {
                'AttributeName': 'UserID',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'Nickname',
                'AttributeType': 'S'
            },
        ],

        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )

def create_articles():
    dynamodb.create_table(
        TableName='articles',

        KeySchema=[
            {
                'AttributeName': 'ArticleID',
                'KeyType': 'HASH'
            },
        ],

        GlobalSecondaryIndexes=[
            {
                'IndexName': 'TagIndex',
                'KeySchema': [
                    {
                        'AttributeName': 'Tag',
                        'KeyType': 'HASH'
                    },
                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 2,
                    'WriteCapacityUnits': 2
                }
            },

            {
                'IndexName': 'StarterIndex',
                'KeySchema': [
                    {
                        'AttributeName': 'StarterID',
                        'KeyType': 'HASH'
                    },
                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 2,
                    'WriteCapacityUnits': 2
                }
            }
        ],

        AttributeDefinitions=[
            {
                'AttributeName': 'ArticleID',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'Tag',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'StarterID',
                'AttributeType': 'S'
            },
        ],

        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )


def create_chapters():
    dynamodb.create_table(
        TableName='chapters',

        KeySchema=[
            {
                'AttributeName': 'ChapterID',
                'KeyType': 'HASH'
            },
        ],

        GlobalSecondaryIndexes=[
            {
                'IndexName': 'ArticleIndex',
                'KeySchema': [
                    {
                        'AttributeName': 'ArticleID',
                        'KeyType': 'HASH'
                    },
                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 2,
                    'WriteCapacityUnits': 2
                }
            },

            {
                'IndexName': 'AuthorIndex',
                'KeySchema': [
                    {
                        'AttributeName': 'AuthorID',
                        'KeyType': 'HASH'
                    },
                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 2,
                    'WriteCapacityUnits': 2
                }
            }
        ],

        AttributeDefinitions=[
            {
                'AttributeName': 'ChapterID',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'ArticleID',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'AuthorID',
                'AttributeType': 'S'
            },
        ],

        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )


def create_comments():
    dynamodb.create_table(
        TableName='comments',

        KeySchema=[
            {
                'AttributeName': 'CommentID',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'ChapterID',
                'KeyType': 'RANGE'
            }
        ],

        GlobalSecondaryIndexes=[
            {
                'IndexName': 'ChapterIndex',
                'KeySchema': [
                    {
                        'AttributeName': 'ChapterID',
                        'KeyType': 'HASH'
                    },
                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 2,
                    'WriteCapacityUnits': 2
                }
            },

            {
                'IndexName': 'CommenterIndex',
                'KeySchema': [
                    {
                        'AttributeName': 'CommenterID',
                        'KeyType': 'HASH'
                    },
                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 2,
                    'WriteCapacityUnits': 2
                }
            }
        ],

        AttributeDefinitions=[
            {
                'AttributeName': 'CommentID',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'ChapterID',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'CommenterID',
                'AttributeType': 'S'
            },
        ],

        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )


def delete_table(tableName):
    dynamodb = boto3.client('dynamodb', region_name='us-east-1', endpoint_url="http://localhost:8000")
    if tableName is not None:
        dynamodb.delete_table(
            TableName=tableName
        )



if __name__ == '__main__':
    # delete_table('users')
    # create_users()
    # delete_table('articles')
    # create_articles()
    # delete_table('chapters')
    create_chapters()