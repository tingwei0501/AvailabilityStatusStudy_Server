from flask import Flask, request, json
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'statusStudy'
app.config['MONGO_URI'] = 'mongodb://localhost/statusStudy'

mongo = PyMongo(app)


@app.route('/', methods=['POST', 'GET'])
def hello():
    return "Hello World!"

@app.route('/idCheck', methods=['POST'])
def idCheck():
    collection = mongo.db.user
    json_request = request.get_json(force=True, silent=True)
    print (json_request)
    userId = json_request['id']
    if collection.count({'id':userId}) == 0:
        message = "可以使用此帳號"
    else:
        message = "此帳號已經存在，請用別的帳號"
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
   
        #message = json.dumps({'response':'ok'})
        message = userId + " 註冊成功"
    return json.dumps({'response':message})

@app.route('/signIn', methods=['POST'])
def signIn():
    collection = mongo.db.user
    json_request = request.get_json(force=True, silent=True)
    print ("sign in: ", json_request)
    userId = json_request['id']
    userPassword = json_request['password']
    data = collection.find({'id': userId})
    message = ''
    if data.count() == 0:
        print ('no user')
        message = "no user"
    else:
        for item in data:
            if item['password'] == userPassword:
                print ("success")
                message = "success" 
            else:
                print ("failed")
                message = "failed"
    #message = json.dumps({'response':'exist'})
    return json.dumps({'response':message})



if __name__ == '__main__':
    app.run(host="172.31.11.127")
