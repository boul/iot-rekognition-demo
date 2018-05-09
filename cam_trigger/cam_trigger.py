import boto3
import json
import os

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

patch_all()

region = os.environ['IOT_REGION']
client = boto3.client('iot-data', region_name=region)

def lambda_handler(event, context):
    
    response = client.publish(
    topic='picture/trigger',
    qos=1,
    payload='{"message": "trigger"}'
    )
    
    return {"body": json.dumps(response), "statusCode": 200}
