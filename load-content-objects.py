import boto3
import json
import uuid
import datetime
from decimal import Decimal

dynamodb = boto3.resource('dynamodb', 'us-east-2')
table = dynamodb.Table('mindstreams-content-objects')

objects = [
  '{"contentId":"c324824e-0ce5-4738-adcb-6736b943b111","kind":"curriculum.content.video","url":"https:\/\/www.udemy.com\/02e9db8a-07af-4b30-b4ec-99afa07e32b0","app":{"app_name":"course:course_taking","app_country":"US"},"page":{"url":"https:\/\/www.udemy.com\/course\/csharp-tutorial-for-beginners\/learn\/lecture\/2936428#overview","path":"\/course\/csharp-tutorial-for-beginners\/learn\/lecture\/2936428","kind":"curriculum.content.video","tags":["videos","k12"]},"product":{"course":"CS229: Machine Learning","provider":"Stanford University","description":"This course provides a broad introduction to machine learning and statistical pattern recognition. Topics include: supervised learning (generative\/discriminative learning, parametric\/non-parametric learning, neural networks, support vector machines); unsupervised learning (clustering, dimensionality reduction, kernel methods); learning theory (bias\/variance tradeoffs, practical advice); reinforcement learning and adaptive control. The course will also discuss recent applications of machine learning, such as to robotic control, data mining, autonomous navigation, bioinformatics, speech recognition, and text and web data processing.","kind":"university_class","level":"undergraduate","field":"computer_science","area":"machine_learning","created":"2019-06-21","updated":"2021-04-25","isActive":true,"links":{"info":"http:\/\/cs229.stanford.edu\/index.html#info","syllabus":"http:\/\/cs229.stanford.edu\/syllabus-spring2021.html","curriculum":"https:\/\/cs.stanford.edu\/degrees\/undergrad\/CurriculumRevision-Overview-09-26-08.pdf"}},"topic":{"id":"Gradient_descent","uri":"https:\/\/en.wikipedia.org\/wiki\/Gradient_descent","name":"Gradient Descent"}}'
]

for i in range(len(objects)):
  obj = objects[i]
  item = json.loads(obj, parse_float=Decimal)
  table.put_item(Item = item)
  print(item)