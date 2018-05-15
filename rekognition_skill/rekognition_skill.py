import json
import time
import uuid
import boto3
import os
import urllib.request
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

patch_all()

api_url = region = os.environ['API_URL']
img_url = region = os.environ['IMG_URL']

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_std_speechlet_response(title, output, reprompt_text,
    should_end_session, l_img_url, s_img_url):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Standard',
            'title': title,
            'text': output,
            "image": {
                "smallImageUrl": s_img_url,
                "largeImageUrl": l_img_url
      }
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to this demo! I'm able to analyse your face! " \
        "But can also tell you with items I can see in the area! " \
        "You can ask me to take a picture, to analyse your face " \
        "or what else i can see!"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Start by asking me to take a picture!"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Bye thanks for joining this demo!"
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

@xray_recorder.capture('## get_rekogniton_output')
def get_rekogniton_output(api_url):
    
    request_headers = {
    "Content-type": "application/json"
    }

    result_url = api_url + "results"
    print(result_url)
    req = urllib.request.Request(result_url, headers=request_headers)
    response = urllib.request.urlopen(req)
    result = response.read()
    
    print(result)
    output = json.loads(result)
    
    return(output)

@xray_recorder.capture('## trigger_cam')    
def trigger_cam(api_url):
    
    request_headers = {
    "Content-type": "application/json"
    }

    result_url = api_url + "trigger"
    print(result_url)
    req = urllib.request.Request(result_url, headers=request_headers)
    response = urllib.request.urlopen(req)
    result = response.read()
    
    print(result)
    output = json.loads(result)
    
    return(output)

@xray_recorder.capture('## label_analysis')
def label_analysis(intent, session):
    session_attributes = {}
    reprompt_text = None
    card_title = "Item Analysis"
    
    output = get_rekogniton_output(api_url)
    
    
    print(output)
    labels = output["labels"]
    print(labels)
    speech_output = "I see the following items: \n"
    if labels['Labels']:
        
        for label in labels['Labels']:
            
            print(label)
            
            speech_output = speech_output + label['Name'] + " with " + \
                str(int(label['Confidence'])) + " percent confidence. \n"
            print("speech :" + speech_output)
        
        should_end_session = False

    else:
       
        speech_output = "I was not able to see any items." \
            "Ask me to take a new picture!"
        should_end_session = False

    output = speech_output
   
    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_std_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session, img_url, 
        img_url))  

@xray_recorder.capture('## face_analysis')        
def face_analysis(intent, session):
    session_attributes = {}
    reprompt_text = None
    card_title = "Face Analysis"
    
    output = get_rekogniton_output(api_url)
    
    
    print(output)
    try:
        first_face = output["faces"]["FaceDetails"][0]
        print(json.dumps(first_face))
    
        if first_face['Confidence']:
            
            gender = first_face['Gender']['Value']
            gender_conf = int(first_face['Gender']['Confidence'])
            age_low = first_face['AgeRange']['Low']
            age_high =  first_face['AgeRange']['High']
            age_avg = (age_high + age_low) / 2
            eyeglasses = first_face['Eyeglasses']['Value']
            smile = first_face['Smile']['Value']
            smile_conf = first_face["Smile"]['Confidence']
            beard = first_face['Beard']['Value']
            mustache = first_face['Mustache']['Value']
            emotion0 = first_face['Emotions'][0]['Type']
            emotion0_confidence = int(first_face['Emotions'][0]['Confidence'])
            emotion1 = first_face['Emotions'][1]['Type']
            emotion1_confidence = int(first_face['Emotions'][1]['Confidence'])
            emotion2 = first_face['Emotions'][2]['Type']
            emotion2_confidence = int(first_face['Emotions'][2]['Confidence'])
            
            
            gender_output = "I'm for " + str(gender_conf) + \
                " percent certain, that you are a " + gender + ".\n"
            age_output = "You are roughly " + str(int(age_avg)) + \
                " years old. \n"
            
            # print("gender" + gender_output)
            # print("age" + age_output)
            
            if smile:
                smile_output = "It seems that you are smiling. \n"
            else:
                smile_output = "It seems that you are not smiling. \n"
                
            if eyeglasses:
                eyeglasses_output = "I see that you are wearing nice"\
                    "glasses! \n"
            else:
                eyeglasses_output = ""
                
            if beard:
                beard_output = "You have a nice beard too! \n"
            else:
                beard_output = ""
                
            if mustache:
                mustache_output = "Wow! you have an awesome moustache! \n"
            else:
                mustache_output = ""
                
            emotion_output = "When looking at your emotions: I see you are " + \
                str(emotion0_confidence) + \
                " percent " + str(emotion0).lower() + ", " + \
                str(emotion1_confidence) + \
                " percent " + str(emotion1).lower() + " and " + \
                str(emotion2_confidence) + \
                " percent " + str(emotion2).lower() + ". \n"
                
                
            speech_output = gender_output + age_output + smile_output + \
                eyeglasses_output + beard_output + mustache_output + \
                emotion_output
               
            print("speech :" + speech_output)    
            should_end_session = False

    except IndexError as e:
       
        print(e)
        speech_output = "I was not able to see your face."\
          " Ask me to take a new picture!"
        should_end_session = False

    output = speech_output
   
    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_std_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session, 
        img_url, img_url))

@xray_recorder.capture('## take_picture')        
def take_picture(intent, session):
    
    session_attributes = {}
    reprompt_text = None
    
    
    trigger_cam(api_url)
    session_attributes = {}
    card_title = "Take Picture"
    speech_output = "Say Cheese!! And smile! I've sent the request to take a new picture!"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = None
    should_end_session = False
    return build_response(session_attributes, build_std_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session, 
        img_url, img_url))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])

def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()

def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "FaceAnalysis":
        return face_analysis(intent, session)
    elif intent_name == "TakePicture":
        return take_picture(intent, session)
    elif intent_name == "LabelAnalysis":
        return label_analysis(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or \
        intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")
    print(event)
    print(context)

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


