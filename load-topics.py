import boto3
import json
import uuid
import datetime
from decimal import Decimal

dynamodb = boto3.resource('dynamodb', 'us-east-2')
table = dynamodb.Table('mindstreams-topics')

topics = [
  '{"topicId":"Gradient_descent","uri":"https:\/\/en.wikipedia.org\/wiki\/Gradient_descent","name":"Gradient Descent","categories":["Mathematical optimization","First order methods","Optimization algorithms and methods","Gradient methods"],"relatedTopics":["Backtracking line search","Conjugate gradient method","Stochastic gradient descent","Rprop","Delta rule","Wolfe conditions","Preconditioning","Broyden\u2013Fletcher\u2013Goldfarb\u2013Shanno algorithm","Davidon\u2013Fletcher\u2013Powell formula","Nelder\u2013Mead method","Gauss\u2013Newton algorithm","Hill climbing","Quantum annealing"]}' 
]

for i in range(len(topics)):
  topic = topics[i]
  obj = json.loads(topic, parse_float=Decimal)
  table.put_item(Item = obj)
  print(obj)