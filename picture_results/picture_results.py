import boto3
import json

client = boto3.client('iot-data')

def lambda_handler(event, context):
    
    response = client.get_thing_shadow(thingName='roeland-greengrass1_Core')
 
    streamingBody = response["payload"]
    jsonState = json.loads(streamingBody.read())
    
    # print(jsonState['state']['reported'])
    
    body = jsonState['state']['reported']
    return {"body": json.dumps(body), "statusCode": 200}
