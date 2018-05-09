import boto3
import json
import os
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

patch_all()

thing_name = os.environ['THING_NAME']
region = os.environ['IOT_REGION']

client = boto3.client('iot-data', region_name=region)

def lambda_handler(event, context):
    
    response = client.get_thing_shadow(thingName=thing_name)
 
    streamingBody = response["payload"]
    jsonState = json.loads(streamingBody.read())
    
    # print(jsonState['state']['reported'])
    
    body = jsonState['state']['reported']
    return {"body": json.dumps(body), "statusCode": 200}
