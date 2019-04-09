
from __future__ import print_function
import json
import datetime
import random

from boto3.dynamodb.conditions import Key, Attr
import boto3
from botocore.exceptions import ClientError


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

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "orangecap":
        return get_orangecap()
    elif intent_name == "standings":
        return get_standings(intent_request)
    elif intent_name == "AMAZON.HelpIntent":
        return get_help_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        return handle_invalid_end_request()


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# --------------- Functions that control the skill's behavior ------------------


def get_welcome_response():

    session_attributes = {}
    card_title = "Welcome"
    CurrentDate = datetime.datetime.today().strftime('"%Y-%m-%d"')
    ExpectedDate = datetime.datetime(2019, 3, 23) 
    if str(CurrentDate) < str(ExpectedDate):
        speech_output = " Welcome to the Orange Cap skill. I can tell about who is owning the IPL2019 Orange Cap. IPL will begin at March Twenty Three 2019. Please come back after March Twenty Third to know who is currently holding the Orange Cap."
    else:
        name = get_firststandingsdb(1)
        speech_output = "Welcome to the Orange Cap skill. Currently " + name + " is holding the Orange Cap. I can also tell first five player positions and scores. Ask for help now. "
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with the same text.
    reprompt_text = speech_output
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


def get_help_response():
    session_attributes = {}
    card_title = "Help"
    speech_output = "I can help you with these type of questions. Examples like, Who is in third position, Who is having orange cap, Who is in second position in Orange cap. Lets get started now by trying one of these. "

    reprompt_text = speech_output
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(card_title,speech_output,reprompt_text,should_end_session))


def get_orangecap():
    session_attributes = {}
    card_title = "FirstStanding"
    CurrentDate = datetime.datetime.today().strftime('"%Y-%m-%d"')
    ExpectedDate = datetime.datetime(2019, 3, 23) 
    if str(CurrentDate) < str(ExpectedDate):
        speech_output = " Welcome to the Orange Cap skill. I can tell about who is owning the IPL2019 Orange Cap. IPL will begin at March Twenty Three 2019. Please come back after March Twenty Third to know who is  holding the Orange Cap."
    else:
        name = get_firststandingsdb(1)
    
        rndmexpression = ['Brilliant!!','Thats great!!','Terrific!!','Amazing!','Wonderful']
        secure_random = random.SystemRandom() 
        expres_name = secure_random.choice(rndmexpression)
        speech_output = "Orange Cap is with the player, " + name + ". " + expres_name
    
    reprompt_text = speech_output
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(card_title,speech_output,reprompt_text,should_end_session))


def get_standings(intent_request):
    session_attributes = {}
    card_title = "PlayerScore"
    CurrentDate = datetime.datetime.today().strftime('"%Y-%m-%d"')
    ExpectedDate = datetime.datetime(2019, 3, 23) 
    if str(CurrentDate) < str(ExpectedDate):
        speech_output = " Welcome to the Orange Cap skill. I can tell about who is owning the IPL2019 Orange Cap. IPL will begin at March Twenty Three 2019. Please come back after March Twenty Third to know who is holding the Orange Cap."
    else:
        speech_output = ""
        player_postion = intent_request["intent"]["slots"]["pname"]["value"]
 
    #print("This is value that is being compared "+ player_postion)
    
        if player_postion == "one" or player_postion == "first" or player_postion == "1st" or player_postion == "1":
            speech_output = get_standingsdb(1)
        elif player_postion == "two" or player_postion == "second" or player_postion == "2nd" or player_postion == "2":
            speech_output = get_standingsdb(2)
        elif player_postion == "three" or player_postion == "third" or player_postion == "3rd" or player_postion == "3":
            speech_output = get_standingsdb(3)
        elif player_postion == "four" or player_postion == "fourth" or player_postion == "4th" or player_postion == "4":
            speech_output = get_standingsdb(4)
        elif player_postion == "five" or player_postion == "fifth" or player_postion == "5th" or player_postion == "5":
            speech_output = get_standingsdb(5)
        else:
            speech_output = "Sorry, I can only help from number one to number five player postions. You can ask me from one to five position and I can answer "
        #print(speech_output)
    reprompt_text = speech_output

    should_end_session = False

    return build_response(session_attributes, build_speechlet_response(card_title,speech_output,reprompt_text,should_end_session))



def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for using the Orange Cap skill! We hope you to hear you again!"
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def handle_invalid_end_request():
    card_title = "Good Bye"
    speech_output = "I hope that is not for me. Good bye!. We hope you to hear you again!"
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))       


# --------------- Helpers that build all of the responses ----------------------


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


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

#Code for DynamoDB begins
#########################




def get_standingsdb(rrank):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('orange')
    try:
        a = str(rrank)
        #print("This is the value sent in the dynamodb table" + a)
        response = table.query(
            KeyConditionExpression=Key('pposition').eq(a)
        )
        for idx, item in enumerate(response['Items']):
            pname = item['playername']
            pposit = item['pposition']
            team = item['pteam']
            sscore = item['score']
            ccomment = item['comment']
            #print(pname,pposit,team,sscore,ccomment)
        return pname + " is in number " + pposit + " position, from " + team + " team. He has scored " + sscore + " runs. " + ccomment
    except ClientError as e:
        print(e.response)

def get_firststandingsdb(rrank):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('orange')
    try:
        a = str(rrank)
        #print("This is the value sent in the dynamodb table" + a)
        response = table.query(
            KeyConditionExpression=Key('pposition').eq(a)
        )
        for idx, item in enumerate(response['Items']):
            pname = item['playername']
            #print(pname)
        return pname
    except ClientError as e:
        print(e.response)