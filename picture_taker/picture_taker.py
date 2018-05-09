
import greengrasssdk
import platform
import time
import json
import picamera
import boto3
import os
from time import sleep

# Creating a greengrass core sdk client
client = greengrasssdk.client('iot-data')

# Retrieving platform information to send from Greengrass Core
my_platform = platform.platform()

region = os.environ['REKOGNITION_REGION']
bucket = os.environ['S3_BUCKET_NAME']
thingname = os.environ['THING_NAME']

def lambda_handler(event, context):
    
    make_picture()
   
    client.publish(topic='picture/status', payload='Picture taken!')
    s3 = boto3.resource('s3')

    # s3.meta.client.upload_file('/output/lambda-image.png', 'roeland-greengrass', 'image.png')
    s3.meta.client.upload_file('/output/lambda-image.png', bucket, 'image.png')
    rekogclient = boto3.client('rekognition', region)

    labels = rekogclient.detect_labels(
        Image={"S3Object": {
                "Bucket": bucket,
                "Name": "image.png",}
             	},
             )
             	
    faces = rekogclient.detect_faces(
        Image={"S3Object": {
                "Bucket": bucket,
                "Name": "image.png",}
             	},
             	Attributes=['ALL'],)
    
    reported = {
        'state':{'reported':{'faces':{},'labels':{}},'desired':{}}
        
    }
    
    # print(faces)
    # print(labels)
    
    reported['state']['reported']['faces'] = faces
    reported['state']['reported']['labels'] = labels
    jsonresponse = json.dumps(reported)
   
    # print reported
    # client.publish(topic='$aws/things/roeland-greengrass1_Core/shadow/update', payload=jsonresponse)
    client.update_thing_shadow(thingname, jsonresponse)
    return

# @xray_recorder.capture('## make_picture')
def make_picture():

    client.publish(topic='picture/status', payload='About to take picture')
    
    try:
        
        # PiCam client
        camera = picamera.PiCamera()
        camera.start_preview()
        # Camera warm-up time
        sleep(2)
        camera.capture('/output/lambda-image.png')
   
    except Exception as e:
        client.publish(topic='picture/status', payload='Something went wrong!')
        print(e)
   
    finally:
        camera.close()
    
    return