from flask import Flask, request, json
from flask_pymongo import PyMongo
import time
import random
import base64
import os

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'statusStudy'
app.config['MONGO_URI'] = 'mongodb://localhost/statusStudy'

mongo = PyMongo(app)

ISOTIMEFORMAT = '%Y-%m-%d %H:%M:%S'

@app.route('/', methods=['POST', 'GET'])
def hello():
    return "Hello World!"

@app.route('/storeSelfStatus', methods=['POST'])
def storeSelfStatus():
    collection = mongo.db.dump
    json_request = request.get_json(force=True, silent=True)
    print (json_request)
    ##### get: {'id': 'tingwei', 'status': 30, 'presentWay': 'digit', 'createdTime': 1557294395291}
    ##### need to insert 5/8 #####
    try:
        collection.insert(json_request)
    except Exception as e:
        print (e)
        message = {'response': 'failed'}
    else:
        message = {'response': 'success insert'}
    
    return json.dumps(message)

@app.route('/getContactStatus', methods=['POST'])
def getContactStatus():
    collection = mongo.db.dump
    json_request = request.get_json(force=True, silent=True)
    print (json_request)
    contactId = json_request['id']

    data = collection.find({'id': contactId})
    res = data.sort('createdTime', -1).limit(1)

    for item in res:
        if ('presentWay' in item and 'status' in item and 'statusText' in item and 'statusColor' in item):
            message = {'presentWay': item['presentWay'], 'status': item['status'], 'createdTime': item['createdTime'], 'statusText': item['statusText'], 'statusColor': item['statusColor']}
        else:
            message = {'response': 'not found data'}
    
    # print ("return message >>>>>>>>>>", message)

    return json.dumps(message)

@app.route('/getSelfStatus', methods=['POST'])
def getStatus():

    collection = mongo.db.dump
    json_request = request.get_json(force=True, silent=True)
    # print (json_request)

    status = random.choice([10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 90, 95])
    presentWay = random.choice(['text', 'digit', 'graphic'])
    createdTime = time.time() * 1000
    statusColor = -13408615  # default color

    json_request['status'] = status
    json_request['createdTime'] = createdTime
    json_request['timeString'] = time.strftime(ISOTIMEFORMAT, time.localtime())
    json_request['presentWay'] = presentWay
    json_request['statusColor'] =  statusColor 
    if status<50 and (presentWay=='text'):
        json_request['statusText'] = '回覆率低'
        statusText = '回覆率低'
    elif status>50 and (presentWay=='text'):
        json_request['statusText'] = '回覆率高'
        statusText = '回覆率高'
    else:
        json_request['statusText'] = ''
        statusText = ''

    # print ("after: ", json_request)
    ##### store to database #####
    collection.insert(json_request)

    return json.dumps({'status': status, 'createdTime': createdTime, 'presentWay': presentWay, 'statusText': statusText, 'statusColor': statusColor})

@app.route('/getList', methods=['POST'])
def getList():
    collection = mongo.db.user
    json_request = request.get_json(force=True, silent=True)
    print (json_request)
    userId = json_request['id']
    data = collection.find({'id':userId})

    message = dict()
    doc = list()
    if data.count() != 0:
        message['response'] = 'success'
        for d in data:
            group = d['group']
        contactList = collection.find({'group':group}, {'_id':0, 'img':0})
        for c in contactList:
            #if 'img' in c:
                #image = c['img']
                #decodeImg = image.decode()
                #c['img'] = decodeImg
            doc.append(c)
            
        message['list'] = doc
    else:
        message['response'] = 'failed'
        
    return json.dumps(message)

@app.route('/idCheck', methods=['POST'])
def idCheck():
    collection = mongo.db.user
    json_request = request.get_json(force=True, silent=True)
    print (json_request)
    userId = json_request['id']
    if collection.count({'id': userId}) == 0:
        message = "success"
    else:
        message = "failed"

    return json.dumps({'response': message})

@app.route('/signUp', methods=['POST'])
def signUp():
    collection = mongo.db.user
    json_request = request.get_json(force=True, silent=True)
    print (json_request)
    userId = json_request['id']
    
    if collection.count({'id': userId}) != 0:
        message = "failed"
    else:
        ### add image
        #imgFile = 'images/' + userId + '.jpg'
        #if os.path.isfile(imgFile):
            #with open(imgFile, "rb") as image_file:
                #encoded_string = base64.b64encode(image_file.read())
            #json_request['img'] = encoded_string
        message = "success"
        #else:
            #message = "image not found"

        collection.insert(json_request)

    return json.dumps({'response':message})

@app.route('/signIn', methods=['POST'])
def signIn():
    collection = mongo.db.user
    json_request = request.get_json(force=True, silent=True)
    print ("sign in: ", json_request)
    userId = json_request['id']
    userPassword = json_request['password']
    data = collection.find({'id': userId})
    if data.count() == 0:
        message = "no user"
    else:
        for item in data:
            if item['password'] == userPassword:
                message = "success" 
            else:
                message = "failed"
                
    return json.dumps({'response':message})

if __name__ == '__main__':
    app.run(host="172.31.11.127")
