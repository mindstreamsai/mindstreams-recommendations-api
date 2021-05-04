from flask import Flask, render_template, request
import json
import boto3
from botocore.exceptions import ClientError
import tempfile
from time import perf_counter
import time
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

recent_recommendations = {}

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
    print(response)
    meta = (response and response["ResponseMetadata"]) or None
    status_code = (meta and meta.get("HTTPStatusCode")) or 500
    if status_code == 200:
        item = response.get("Item", None)
        user_data = (item and clean_json(response["Item"])) or None
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
    user_id = None
    request_data = request.get_data()
    data = json.loads(request_data)

    user_id = data["userId"]
    user_data = get_latest_scores_for_user(user_id)
    if user_data is None:
        return {}

    clean_data = clean_json(user_data)

    context = data["context"]
    content = (context and context["content"]) or None
    video_status = (content and content["status"]) or None
    video_speed = (content and content["speed"]) or 0

    user_context = context.get("user", None)
    user_last_interaction_time = 0
    if user_context is not None:
        user_last_interaction_time = user_context.get("lastInteractionTime", 0) / 1000

    user_scores = user_data["scores"]

    user_learning_rate = user_scores["learning_rate"]
    user_cognitive_presence = user_scores["cognitive_presence"]
    recommended_speed = user_learning_rate

    data = '{"id":"6120894d-0ce5-4738-adcb-6736b943b202","sessionId":"7ac9cfd9-db52-429a-a621-2e43dba7a267","userId":"austinbeaudreau@gmail.com","ts":"2021-04-25T19:15:39.301251","status":200,"context":{"app":{"app_name":"course:course_taking","app_country":"US"},"page":{"url":"https:\/\/www.udemy.com\/course\/csharp-tutorial-for-beginners\/learn\/lecture\/2936428#overview","path":"\/course\/csharp-tutorial-for-beginners\/learn\/lecture\/2936428","kind":"curriculum.content.video","tags":["videos","k12"]},"topic":{"id":"Gradient_descent","uri":"https:\/\/en.wikipedia.org\/wiki\/Gradient_descent","name":"Gradient Descent"},"content":{"contentId":"c324824e-0ce5-4738-adcb-6736b943b111","kind":"curriculum.content.video","url":"https:\/\/www.udemy.com\/02e9db8a-07af-4b30-b4ec-99afa07e32b0"}},"recommendations":[{"id":"6120894d-0ce5-4738-adcb-6736b943b202","rank":1,"category":"understanding","action":"video.slower","confidence":0.53,"ts":"2021-04-25T19:15:39.301251"},{"id":"3468367d-0ce5-4738-adcb-6736b943b201","rank":2,"category":"engagement","action":"game.trivia","confidence":0.48,"ts":"2021-04-25T19:15:39.301251"},{"id":"6120894d-0ce5-4738-adcb-6736b943b202","rank":3,"category":"understanding","action":"feedback.ask","confidence":0.34,"ts":"2021-04-25T19:15:39.301251"},{"id":"3468367d-0ce5-4738-adcb-6736b943b201","rank":4,"category":"understanding","action":"video.push","context":{"contentId":"7a7d4908-3a33-41f3-909c-c6693b11ee63","kind":"curriculum.content.video","title":"C# Arrays vs. LUA Tables","duration":157,"prompt":true,"trigger":{"kind":"video.playback","position":108},"objective":"comparison_learning","url":"https:\/\/www.udemy.com\/720fdb8a-07af-4b30-b4ec-99afa07e32b0"},"confidence":0.31,"ts":"2021-04-25T19:15:39.301251"}]}';

    user_actions = recent_recommendations.get(user_id, None)
    if user_actions is None:
        user_actions = {}
        recent_recommendations[user_id] = user_actions

    current_time = time.time()
    last_interaction_seconds_ago = current_time - user_last_interaction_time
    print(last_interaction_seconds_ago)
    recommended_actions = []
    action = None
    if video_status == 'playing':
        if (user_cognitive_presence < 0.3) and (last_interaction_seconds_ago > 30):
            last_time = user_actions.get("presence.ask", None)
            if last_time is None:
                user_actions["presence.ask"] = time.time() - 45
            elif (current_time - last_time) > 60:
                action = {
                    "category": "understanding",
                    "action": "presence.ask"
                }
        elif recommended_speed > video_speed:
            action = {
                "category": "understanding",
                "action": "video.faster",
                "speed": recommended_speed
            }
        elif recommended_speed < video_speed:
            action = {
                "category": "understanding",
                "action": "video.slower",
                "speed": recommended_speed
            }
    elif video_status == 'paused':
        if (user_cognitive_presence > 0.7) and (last_interaction_seconds_ago > 15):
            print('** SUPPLEMENTAL **')
            last_time = user_actions.get("topic.supplemental_content", None)
            print(last_time)
            if last_time is None:
                user_actions["topic.supplemental_content"] = time.time()
            delta_time = time.time() - (last_time or 0)
            if delta_time > 60:
                user_actions["topic.supplemental_content"] = time.time()                
                action = {
                    "category": "understanding",
                    "action": "topic.supplemental_content"
                }
        else:
            action = {
                "category": "understanding",
                "action": "video.resume"
            }

    if action is not None:
        action["id"] = str(uuid.uuid4())
        action["rank"]: 1
        action["confidence"]: random.random()
        action["ts"]: datetime.datetime.now().isoformat()
        recommended_actions.append(action)
        user_actions["presence.ask"] = time.time()

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