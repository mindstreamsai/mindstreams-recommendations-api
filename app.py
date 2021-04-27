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
 
BUCKET = 'mindstreams'

app = Flask(__name__)
s3 = boto3.client('s3')

possible_actions = [
    "video.slower",
    "video.faster",
    "video.pause",
    "video.resume",
    "video.play",
    "game.trivia",
    "feedback.ask"    
]

list_of_recommendaitons = [
    {"id":"6120894d-0ce5-4738-adcb-6736b943b202","rank":1,"category":"understanding","action":"video.slower","confidence":0.53,"ts":"2021-04-25T19:15:39.301251"},
    {"id":"3468367d-0ce5-4738-adcb-6736b943b201","rank":2,"category":"engagement","action":"game.trivia","confidence":0.48,"ts":"2021-04-25T19:15:39.301251"},
    {"id":"6120894d-0ce5-4738-adcb-6736b943b202","rank":3,"category":"understanding","action":"feedback.ask","confidence":0.34,"ts":"2021-04-25T19:15:39.301251"},
]

@app.route('/api/content/<content_id>', methods=['GET'])
def mindstream_get_content(content_id):
    data = '{"contentId":"c324824e-0ce5-4738-adcb-6736b943b111","kind":"curriculum.content.video","url":"https:\/\/www.udemy.com\/02e9db8a-07af-4b30-b4ec-99afa07e32b0","app":{"app_name":"course:course_taking","app_country":"US"},"page":{"url":"https:\/\/www.udemy.com\/course\/csharp-tutorial-for-beginners\/learn\/lecture\/2936428#overview","path":"\/course\/csharp-tutorial-for-beginners\/learn\/lecture\/2936428","kind":"curriculum.content.video","tags":["videos","k12"]},"product":{"course":"CS229: Machine Learning","provider":"Stanford University","description":"This course provides a broad introduction to machine learning and statistical pattern recognition. Topics include: supervised learning (generative\/discriminative learning, parametric\/non-parametric learning, neural networks, support vector machines); unsupervised learning (clustering, dimensionality reduction, kernel methods); learning theory (bias\/variance tradeoffs, practical advice); reinforcement learning and adaptive control. The course will also discuss recent applications of machine learning, such as to robotic control, data mining, autonomous navigation, bioinformatics, speech recognition, and text and web data processing.","kind":"university_class","level":"undergraduate","field":"computer_science","area":"machine_learning","created":"2019-06-21","updated":"2021-04-25","isActive":true,"links":{"info":"http:\/\/cs229.stanford.edu\/index.html#info","syllabus":"http:\/\/cs229.stanford.edu\/syllabus-spring2021.html","curriculum":"https:\/\/cs.stanford.edu\/degrees\/undergrad\/CurriculumRevision-Overview-09-26-08.pdf"}},"topic":{"id":"Gradient_descent","uri":"https:\/\/en.wikipedia.org\/wiki\/Gradient_descent","name":"Gradient Descent"}}';
    response = json.loads(data)
    return response


@app.route('/api/content', methods=['GET'])
def mindstream_list_content():
    data = '{"Content": [{"contentId":"c324824e-0ce5-4738-adcb-6736b943b111", "kind":"curriculum.content.video", "url":"https:\/\/www.udemy.com\/02e9db8a-07af-4b30-b4ec-99afa07e32b0"}]}';
    response = json.loads(data)
    return response


@app.route('/api/topics/<topic_id>', methods=['GET'])
def mindstream_get_topic(topic_id):
    data = '{"id":"Gradient_descent","uri":"https:\/\/en.wikipedia.org\/wiki\/Gradient_descent","name":"Gradient Descent","categories":["Mathematical optimization","First order methods","Optimization algorithms and methods","Gradient methods"],"relatedTopics":["Backtracking line search","Conjugate gradient method","Stochastic gradient descent","Rprop","Delta rule","Wolfe conditions","Preconditioning","Broyden\u2013Fletcher\u2013Goldfarb\u2013Shanno algorithm","Davidon\u2013Fletcher\u2013Powell formula","Nelder\u2013Mead method","Gauss\u2013Newton algorithm","Hill climbing","Quantum annealing"]}';
    response = json.loads(data)
    return response


@app.route('/api/topics', methods=['GET'])
def mindstream_list_topics():
    data = '{"Topics": ["Gradient_descent", "Mathematical_optimization", "First_order_methods", "Optimization_algorithms_and_methods", "Gradient_methods", "Backtracking_line_search", "Conjugate_gradient_method", "Stochastic_gradient_descent", "Rprop", "Delta_rule", "Wolfe_conditions", "Preconditioning", "Broyden\u2013Fletcher\u2013Goldfarb\u2013Shanno_algorithm", "Davidon\u2013Fletcher\u2013Powell_formula", "Nelder\u2013Mead_method", "Gauss\u2013Newton_algorithm", "Hill_climbing", "Quantum_annealing"]}';
    response = json.loads(data)
    print(response)
    return response


@app.route('/api/users/<user_id>/recommendations', methods=['POST'])
def mindstream_user_give_recommendations(user_id):
    save = request.get_json()
    data = '{"id":"6120894d-0ce5-4738-adcb-6736b943b202","sessionId":"7ac9cfd9-db52-429a-a621-2e43dba7a267","userId":"austinbeaudreau@gmail.com","ts":"2021-04-25T19:15:39.301251","status":200,"context":{"app":{"app_name":"course:course_taking","app_country":"US"},"page":{"url":"https:\/\/www.udemy.com\/course\/csharp-tutorial-for-beginners\/learn\/lecture\/2936428#overview","path":"\/course\/csharp-tutorial-for-beginners\/learn\/lecture\/2936428","kind":"curriculum.content.video","tags":["videos","k12"]},"topic":{"id":"Gradient_descent","uri":"https:\/\/en.wikipedia.org\/wiki\/Gradient_descent","name":"Gradient Descent"},"content":{"contentId":"c324824e-0ce5-4738-adcb-6736b943b111","kind":"curriculum.content.video","url":"https:\/\/www.udemy.com\/02e9db8a-07af-4b30-b4ec-99afa07e32b0"}},"mindstreams":{"cognitive":{"engagement":0,"interest":0,"focus":0,"relaxation":0,"excitement":0,"stress":0},"facial":{"smiling":0.2,"frowning":0.4,"puzzled":0,"nodding":0.5},"eyes":{"open":0.9,"tracking":0.9,"movement":0.88,"squinting":0.2},"emotions":{"positivity":0.92,"patience":0.83,"annoyance":0.02,"disappointed":0.5},"mental":{"capacity":0.8,"speed":0.99,"memory":0.9,"logic":0.98},"topical":{"sentiment":0.1},"learning":{"rate":0.9,"quality":0.4,"depth":0.1,"breadth":0.5}},"recommendations":[{"id":"6120894d-0ce5-4738-adcb-6736b943b202","rank":1,"category":"understanding","action":"video.slower","confidence":0.53,"ts":"2021-04-25T19:15:39.301251"},{"id":"3468367d-0ce5-4738-adcb-6736b943b201","rank":2,"category":"engagement","action":"game.trivia","confidence":0.48,"ts":"2021-04-25T19:15:39.301251"},{"id":"6120894d-0ce5-4738-adcb-6736b943b202","rank":3,"category":"understanding","action":"feedback.ask","confidence":0.34,"ts":"2021-04-25T19:15:39.301251"},{"id":"3468367d-0ce5-4738-adcb-6736b943b201","rank":4,"category":"understanding","action":"video.push","context":{"contentId":"7a7d4908-3a33-41f3-909c-c6693b11ee63","kind":"curriculum.content.video","title":"C# Arrays vs. LUA Tables","duration":157,"prompt":true,"trigger":{"kind":"video.playback","position":108},"objective":"comparison_learning","url":"https:\/\/www.udemy.com\/720fdb8a-07af-4b30-b4ec-99afa07e32b0"},"confidence":0.31,"ts":"2021-04-25T19:15:39.301251"}]}';

    count = math.floor(random.random() * 4)
    recommended_actions = []
    for i in range(count):
        j = math.ceil(random.random() * len(possible_actions)) - 1
        action = {
            "id": str(uuid.uuid4()),
            "rank": i,
            "category": "understanding",
            "action": possible_actions[j],
            "confidence": random.random(),
            "ts": datetime.datetime.now().isoformat()
        }
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
