from flask import Flask, request, json
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'statusStudy'
app.config['MONGO_URI'] = 'mongodb://localhost/statusStudy'

mongo = PyMongo(app)


@app.route('/', methods=['POST', 'GET'])
def hello():
    return "Hello World!"

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
        contactList = collection.find({'group':group, 'id':{'$ne':userId}}, {'_id':0})
        for c in contactList:
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
    if collection.count({'id':userId}) == 0:
        message = "success"
    else:
        message = "failed"

    return json.dumps({'response':message})

@app.route('/signUp', methods=['POST'])
def signUp():
    collection = mongo.db.user
    json_request = request.get_json(force=True, silent=True)
    print (json_request)
    userId = json_request['id']
    if collection.count({'id':userId}) != 0:
        message = "failed"
    else:
        collection.insert(json_request)
        message = "success"

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
