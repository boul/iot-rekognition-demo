import boto3
import json

client = boto3.client('iot-data')

def lambda_handler(event, context):
    
    response = client.publish(
    topic='picture/trigger',
    qos=1,
    payload='{"message": "trigger"}'
    )
    
    return {"body": json.dumps(response), "statusCode": 200}
