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

@app.route('/storeQuestionnaire', methods=['POST'])
def storeQuestionnaire():
    request_c = str(request.args['collection'])
    json_request = request.get_json(force=True, silent=True)

    if request_c == 'contactQuestionnaire':
        collection = mongo.db.contactQuestionnaire
    elif request_c == 'selfQuestionnaire':
        collection = mongo.db.selfQuestionnaire
    
    try:
        print (json_request)
        ##### insert here #####
        collection.insert(json_request)
    except Exception as e:
        print (e)
        message = {'response': 'failed'}
    else:
        message = {'response': 'success insert'}

    return json.dumps(message)

@app.route('/storeSelfStatus', methods=['POST'])
def storeSelfStatus():
    collection = mongo.db.dump
    json_request = request.get_json(force=True, silent=True)
    print (json_request)
    ##### get: {'user_id': 'tingwei', 'status': 30, 'presentWay': 'digit', 'createdTime': 1557294395291}
    try:
        ##### !!!!! uncomment !!!!! #####
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

    data = collection.find({'user_id': contactId})
    res = data.sort('createdTime', -1).limit(1)

    message = dict()
    editOrNot = False

    for item in res:
        if 'afterEdit' in item: 
            if item['afterEdit']: #有更新
                editOrNot = True 
        if editOrNot:
            if ('presentWayEdit' in item and 'statusEdit' in item and 'statusTextEdit' in item and 'statusColorEdit' in item and 'statusFormEdit' in item):
                print ("in edit")
                message = {'presentWay': item['presentWayEdit'], 'status': item['statusEdit'], 'createdTime': item['createdTimeEdit'], 'statusText': item['statusTextEdit'], 'statusColor': item['statusColorEdit'], 'statusForm': item['statusFormEdit']}
            elif ('presentWay' in item and 'status' in item and 'statusText' in item and 'statusColor' in item):
                message = {'presentWay': item['presentWay'], 'status': item['status'], 'createdTime': item['createdTime'], 'statusText': item['statusText'], 'statusColor': item['statusColor'], 'statusForm': item['statusForm']}
            else:
                message = {'response': 'not found data'}    
        else:
            if ('presentWay' in item and 'status' in item and 'statusText' in item and 'statusColor' in item):
                message = {'presentWay': item['presentWay'], 'status': item['status'], 'createdTime': item['createdTime'], 'statusText': item['statusText'], 'statusColor': item['statusColor'], 'statusForm': item['statusForm']}
            else:
                message = {'response': 'not found data'}


    # print ("return message >>>>>>>>>>", message)

    return json.dumps(message)

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
            if "group" in d:
                group = d['group'] # f no group, use code
                contactList = collection.find({'$or':[{'group':group}, {'code': userId}]}, {'_id':0, 'img':0})
            elif "code" in d:
                print ("### partial subject ###")
                code = d['code']
                contactList = collection.find({'id':code}, {'_id':0, 'img':0})

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
