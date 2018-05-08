
import greengrasssdk
import platform
import time
import json
import picamera
import boto3
from time import sleep

# from aws_xray_sdk.core import xray_recorder
# from aws_xray_sdk.core import patch_all

# patch_all()

# Creating a greengrass core sdk client
client = greengrasssdk.client('iot-data')

# Retrieving platform information to send from Greengrass Core
my_platform = platform.platform()

def lambda_handler(event, context):
    
    make_picture()
   
    client.publish(topic='picture/status', payload='Picture taken!')
    s3 = boto3.resource('s3')

    # s3.meta.client.upload_file('/output/lambda-image.png', 'roeland-greengrass', 'image.png')
    s3.meta.client.upload_file('/output/lambda-image.png', 'roeland-greengrass2', 'image.png')
    rekogclient = boto3.client('rekognition', 'eu-west-1')

    labels = rekogclient.detect_labels(
        Image={"S3Object": {
                "Bucket": "roeland-greengrass2",
                "Name": "image.png",}
             	},
             )
             	
    faces = rekogclient.detect_faces(
        Image={"S3Object": {
                "Bucket": "roeland-greengrass2",
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
    client.publish(topic='$aws/things/roeland-greengrass1_Core/shadow/update', payload=jsonresponse)
      
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