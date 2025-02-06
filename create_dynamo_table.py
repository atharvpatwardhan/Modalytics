import boto3

AWS_REGION = "us-east-1"

dynamodb = boto3.resource('dynamodb',
                         aws_access_key_id='your_aws_access_key',
                         aws_secret_access_key='your_aws_secret_access_key',
                        region_name = AWS_REGION)

user_table = dynamodb.create_table(
    TableName='modalyze-table',
    KeySchema=[
        {
            'AttributeName': 'UserID',
            'KeyType': 'HASH'  # Partition key
        },
        {
            'AttributeName':'UploadDate',
            'KeyType':'RANGE'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'UserID',
            'AttributeType': 'S'
        },
        {
            'AttributeName':'UploadDate',
            'AttributeType':'S'
        }
    ],
    ProvisionedThroughput={
    'ReadCapacityUnits': 5,  # Read capacity units
    'WriteCapacityUnits': 5  # Write capacity units
    }
    )

