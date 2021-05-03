from flask import Flask, render_template, request
import json
import boto3
from botocore.exceptions import ClientError
import tempfile
from time import perf_counter
from dateutil.tz import tzutc
import datetime
import arrow
import random
import math
import uuid
from decimal import Decimal
from flask_cors import CORS
 
BUCKET = 'mindstreams'

app = Flask(__name__)
CORS(app)

s3 = boto3.client('s3')

dynamodb = boto3.resource('dynamodb', 'us-east-2')
table_scores = dynamodb.Table('mindstreams-user-scores')
topic_table = dynamodb.Table('mindstreams-topics')
content_table = dynamodb.Table('mindstreams-content-objects')


possible_actions = [
    "video.slower",
    "video.faster"
]

list_of_recommendaitons = [
    {"id":"6120894d-0ce5-4738-adcb-6736b943b202","rank":1,"category":"understanding","action":"video.slower","confidence":0.53,"ts":"2021-04-25T19:15:39.301251"},
    {"id":"3468367d-0ce5-4738-adcb-6736b943b201","rank":2,"category":"engagement","action":"game.trivia","confidence":0.48,"ts":"2021-04-25T19:15:39.301251"},
    {"id":"6120894d-0ce5-4738-adcb-6736b943b202","rank":3,"category":"understanding","action":"feedback.ask","confidence":0.34,"ts":"2021-04-25T19:15:39.301251"},
]

def clean_json(o): 
    if type(o) == dict:
        for k in o: o[k] = clean_json(o[k])
    elif type(o) == list:
        for i in range(len(o)): o[i] = clean_json(o[i])
    elif type(o) == Decimal:
        o = float(o)
    return o


def get_latest_scores_for_user(user_id):
    user_data = None
    key = { "userId": user_id }
    response = table_scores.get_item(Key = key)
    meta = response["ResponseMetadata"]
    if meta["HTTPStatusCode"]:
        user_data = clean_json(response["Item"])
    return user_data


## Content Index ###
@app.route('/api/content/<content_id>', methods=['GET'])
def mindstream_get_content(content_id):
    content_data = None
    key = { "contentId": content_id }
    response = content_table.get_item(Key = key)
    meta = response["ResponseMetadata"]
    if meta["HTTPStatusCode"]: content_data = clean_json(response["Item"])
    return content_data

@app.route('/api/content', methods=['GET'])
def mindstream_list_content():
    response = content_table.scan()
    data = response['Items']
    while 'LastEvaluatedKey' in response:
        response = content_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])
    return response


### Knowledge Graph ###
@app.route('/api/topics/<topic_id>', methods=['GET'])
def mindstream_get_topic(topic_id):
    topic_data = None
    key = { "topicId": topic_id }
    response = topic_table.get_item(Key = key)
    meta = response["ResponseMetadata"]
    if meta["HTTPStatusCode"]: topic_data = clean_json(response["Item"])
    return topic_data


@app.route('/api/topics', methods=['GET'])
def mindstream_list_topics():
    response = topic_table.scan()
    data = response['Items']
    while 'LastEvaluatedKey' in response:
        response = topic_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])
    return response


### Recommendations ###
@app.route('/api/users/<user_id>/recommendations', methods=['POST'])
def mindstream_user_give_recommendations(user_id):
    request_data = request.get_data()
    data = json.loads(request_data)

    user_id = data["userId"]
    user_data = get_latest_scores_for_user(user_id)
    clean_data = clean_json(user_data)
    print(json.dumps(clean_data, indent=2))

    context = data["context"]
    content = (context and context["content"]) or None
    video_status = (content and content["status"]) or None
    video_speed = (content and content["speed"]) or 0
    print(video_status, video_speed)

    user_scores = user_data["scores"]
    user_learning_rate = user_scores["learning_rate"]
    recommended_speed = user_learning_rate

    candidate_actions = []
    if video_status == 'playing':
        # candidate_actions.append('video.pause')
        if video_speed <= 1.5:
            candidate_actions.append('video.faster')
        if video_speed >= 0.75:
            candidate_actions.append('video.slower')
    elif video_status == 'paused':
        # candidate_actions.append('video.resume')
        candidate_actions.append('game.trivia')
        candidate_actions.append('feedback.ask')

    data = '{"id":"6120894d-0ce5-4738-adcb-6736b943b202","sessionId":"7ac9cfd9-db52-429a-a621-2e43dba7a267","userId":"austinbeaudreau@gmail.com","ts":"2021-04-25T19:15:39.301251","status":200,"context":{"app":{"app_name":"course:course_taking","app_country":"US"},"page":{"url":"https:\/\/www.udemy.com\/course\/csharp-tutorial-for-beginners\/learn\/lecture\/2936428#overview","path":"\/course\/csharp-tutorial-for-beginners\/learn\/lecture\/2936428","kind":"curriculum.content.video","tags":["videos","k12"]},"topic":{"id":"Gradient_descent","uri":"https:\/\/en.wikipedia.org\/wiki\/Gradient_descent","name":"Gradient Descent"},"content":{"contentId":"c324824e-0ce5-4738-adcb-6736b943b111","kind":"curriculum.content.video","url":"https:\/\/www.udemy.com\/02e9db8a-07af-4b30-b4ec-99afa07e32b0"}},"recommendations":[{"id":"6120894d-0ce5-4738-adcb-6736b943b202","rank":1,"category":"understanding","action":"video.slower","confidence":0.53,"ts":"2021-04-25T19:15:39.301251"},{"id":"3468367d-0ce5-4738-adcb-6736b943b201","rank":2,"category":"engagement","action":"game.trivia","confidence":0.48,"ts":"2021-04-25T19:15:39.301251"},{"id":"6120894d-0ce5-4738-adcb-6736b943b202","rank":3,"category":"understanding","action":"feedback.ask","confidence":0.34,"ts":"2021-04-25T19:15:39.301251"},{"id":"3468367d-0ce5-4738-adcb-6736b943b201","rank":4,"category":"understanding","action":"video.push","context":{"contentId":"7a7d4908-3a33-41f3-909c-c6693b11ee63","kind":"curriculum.content.video","title":"C# Arrays vs. LUA Tables","duration":157,"prompt":true,"trigger":{"kind":"video.playback","position":108},"objective":"comparison_learning","url":"https:\/\/www.udemy.com\/720fdb8a-07af-4b30-b4ec-99afa07e32b0"},"confidence":0.31,"ts":"2021-04-25T19:15:39.301251"}]}';

    recommended_actions = []
    action = None
    if recommended_speed > video_speed:
        action = {
            "id": str(uuid.uuid4()),
            "rank": 1,
            "category": "understanding",
            "action": "video.faster",
            "confidence": random.random(),
            "speed": recommended_speed,
            "ts": datetime.datetime.now().isoformat()
        }
    elif recommended_speed < video_speed:
        action = {
            "id": str(uuid.uuid4()),
            "rank": 1,
            "category": "understanding",
            "action": "video.slower",
            "confidence": random.random(),
            "speed": recommended_speed,
            "ts": datetime.datetime.now().isoformat()
        }

    if action is not None:
        recommended_actions.append(action)

    response = json.loads(data)
    response['recommendations'] = recommended_actions
    return response


@app.route('/demo', methods=['GET'])
def get_demo():
    with open('./demo.html') as f:
	    content = f.read(100000)
    print(content)
    response = content
    return response
