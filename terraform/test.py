import boto3
import json
# Get the service resource.
dynamodb = boto3.resource('dynamodb')
# Get the table.
table = dynamodb.Table('post-table')
response = table.scan(
    Select='COUNT',
    ReturnConsumedCapacity='TOTAL',
)
#print(json.dumps(response, indent=2))

u1="elie"
resp = table.query(
    Select='ALL_ATTRIBUTES',
    KeyConditionExpression="user = :us",
    ExpressionAttributeValues={
        ":us": f"USER#{u1}",
    },
)

print(json.dumps(resp, indent=2))