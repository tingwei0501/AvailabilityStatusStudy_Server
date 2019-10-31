from flask import Flask, request, json
from flask_pymongo import PyMongo
import datetime

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'statusStudy'
app.config['MONGO_URI'] = 'mongodb://localhost/statusStudy'

mongo = PyMongo(app)

@app.route('/checkDumpData', methods=['POST'])
def checkDumpData():
    jsonquery = request.get_json(force=True, silent=True)
    query = json.loads(jsonquery)
    user_id = query['id']

    start = datetime.datetime(2019, query['query_start_month'], query['query_start_date']-1, 16)
    end = datetime.datetime(2019, query['query_end_month'], query['query_end_date'], 15, 59, 59)

    collection = mongo.db.dump
    dumpDataCoount = collection.find({'user_id': user_id, 'createdTime': {'$gte': start.timestamp()*1000, '$lt': end.timestamp()*1000} }).count()
    
    message = {'count': dumpDataCoount}
    return json.dumps(message)


@app.route('/checkContactStatusRate', methods=['POST'])
def checkContactStatusRate():
    jsonquery = request.get_json(force=True, silent=True)
    query = json.loads(jsonquery)
    user_id = query['id']
    # convert to UTC+8
    start = datetime.datetime(2019, query['query_start_month'], query['query_start_date']-1, 16)
    end = datetime.datetime(2019, query['query_end_month'], query['query_end_date'], 15, 59, 59)

    collection = mongo.db.contactQuestionnaire
    dataSet = collection.find({'user_id': user_id, 'checkContactStatusTime': {'$gte': start.timestamp()*1000, '$lt': end.timestamp()*1000} })
    count = dict()
    for item in dataSet:
        print (item)
        # print (item['contactId'])
        if item['contactId'] not in count:
            count[item['contactId']] = 1
        else:
            count[item['contactId']] += 1
    for key, value in count.items():
        print (key, " ", value)

    return json.dumps(count)

@app.route('/wordToMe', methods=['POST'])
def wordToMe(): 
    jsonquery = request.get_json(force=True, silent=True)
    query = json.loads(jsonquery)
    user_id = query['id']

    start = datetime.datetime(2019, query['query_start_month'], query['query_start_date']-1, 16)
    end = datetime.datetime(2019, query['query_end_month'], query['query_end_date'], 15, 59, 59)
    collection = mongo.db.contactQuestionnaire
    dataSet = collection.find({'contactId': user_id, 'checkContactStatusTime': {'$gte': start.timestamp()*1000, '$lt': end.timestamp()*1000} })
    word = dict()
    for item in dataSet:
        print (item)
        if item['oneWordToContact'] != "":
            print (item['oneWordToContact'])
            if item['user_id'] not in word:
                word[item['user_id']] = [item['oneWordToContact']]
            else:
                word[item['user_id']].append(item['oneWordToContact'])
            
    for key, val in word.items():
        print (key, ": ", val)

    return json.dumps(word)

@app.route('/whoCheckMyStatus', methods=['POST'])
def whoCheckMyStatus():
    jsonquery = request.get_json(force=True, silent=True)
    query = json.loads(jsonquery)
    user_id = query['id']

    start = datetime.datetime(2019, query['query_start_month'], query['query_start_date']-1, 16)
    end = datetime.datetime(2019, query['query_end_month'], query['query_end_date'], 15, 59, 59)
    collection = mongo.db.contactQuestionnaire
    dataSet = collection.find({'contactId': user_id, 'checkContactStatusTime': {'$gte': start.timestamp()*1000, '$lt': end.timestamp()*1000} })
    whoCheckMe = dict()
    for item in dataSet:
        print (item)
        if item['user_id'] not in whoCheckMe:
            whoCheckMe[item['user_id']] = 1
        else:
            whoCheckMe[item['user_id']] += 1
    for key, val in whoCheckMe.items():
        print (key, val)

    return json.dumps(whoCheckMe)
    
@app.route('/notificationCompletedRate', methods=['POST'])
def notificationCompletedRate():
    total = 0
    selfCompleted = 0
    selfEdit = 0

    jsonquery = request.get_json(force=True, silent=True)
    query = json.loads(jsonquery)
    user_id = query['id']
    # start = datetime.datetime(2019, query['query_start_month'], query['query_start_date'], 0, 0, 0, 0)
    # end = datetime.datetime(2019, query['query_end_month'], query['query_end_date']+1, 0, 0, 0, 0)
    start = datetime.datetime(2019, query['query_start_month'], query['query_start_date']-1, 16)
    end = datetime.datetime(2019, query['query_end_month'], query['query_end_date'], 15, 59, 59)

    # print (start.timestamp())
    # print (end.timestamp())

    collection = mongo.db.selfQuestionnaire
    totalQuestionnaires = collection.find({'user_id': user_id, 'createdTime': {'$gte': start.timestamp()*1000, '$lt': end.timestamp()*1000} })
    for item in totalQuestionnaires:
        if 'completeTime' not in item:
            total += 1
        elif 'completeTime' in item:
            timePeriodInSec = (item['completeTime'] - item['createdTime']) / 1000
            # <= 0.5 hours
            if timePeriodInSec <= 1800: #7200
                if 'idealShowDifferent' in item:
                    selfCompleted += 1
                elif 'changeEventId' in item:
                    selfEdit += 1 
        

    print ("total: ", total)
    print ("selfCompleted: ", selfCompleted)
    print ("selfEdit: ", selfEdit)

    if total>0:
        rate = selfCompleted/total
    else:
        rate = 0
    message = {'total': total, 'selfCompleted': selfCompleted, 'completedRate': rate, 'selfEditCompleted': selfEdit}

    return json.dumps(message)

@app.route('/idealStatusResult', methods=['POST'])
def idealStatusResult():
    jsonquery = request.get_json(force=True, silent=True)
    query = json.loads(jsonquery)
    user_id = query['id']
    # start = datetime.datetime(2019, query['query_start_month'], query['query_start_date'], 0, 0, 0, 0)
    # end = datetime.datetime(2019, query['query_end_month'], query['query_end_date']+1, 0, 0, 0, 0)
    start = datetime.datetime(2019, query['query_start_month'], query['query_start_date']-1, 16)
    end = datetime.datetime(2019, query['query_end_month'], query['query_end_date'], 15, 59, 59)

    collection = mongo.db.selfQuestionnaire
    dataSet = collection.find({'user_id': user_id, 'completeTime': {'$gte': start.timestamp()*1000, '$lt': end.timestamp()*1000} })
    presentWayCount = dict()

    for item in dataSet:
        if 'idealStatusWay' in item:  ####### 已修改!!!! idealStatusWay
            if item['idealStatusWay'] not in presentWayCount:  ####### 已修改!!!! idealStatusWay
                presentWayCount[item['idealStatusWay']] = 1  ####### 已修改!!!! idealStatusWay
            else:
                presentWayCount[item['idealStatusWay']] += 1  ####### 已修改!!!! idealStatusWay
    
    for key, val in presentWayCount.items():
        print (key, ": ", val)

    return json.dumps(presentWayCount)

@app.route('/contactStatusPresentResult', methods=['POST'])
def contactStatusPresentResult():
    jsonquery = request.get_json(force=True, silent=True)
    query = json.loads(jsonquery)
    user_id = query['id']
    # start = datetime.datetime(2019, query['query_start_month'], query['query_start_date'], 0, 0, 0, 0)
    # end = datetime.datetime(2019, query['query_end_month'], query['query_end_date']+1, 0, 0, 0, 0)
    start = datetime.datetime(2019, query['query_start_month'], query['query_start_date']-1, 16)
    end = datetime.datetime(2019, query['query_end_month'], query['query_end_date'], 15, 59, 59)

    collection = mongo.db.contactQuestionnaire
    dataSet = collection.find({'user_id': user_id, 'checkContactStatusTime': {'$gte': start.timestamp()*1000, '$lt': end.timestamp()*1000} })
    contactStatusPresentWayCount = {'幫助判斷對方有空或沒空: 文字': 0, '幫助判斷對方有空或沒空: 數字': 0, '幫助判斷對方有空或沒空: 圖像': 0, '想看到: 文字': 0, '想看到: 數字': 0, '想看到: 圖像': 0}

    for item in dataSet:
        print (item)
        print (item['selectedIsFreeA'])
        contactStatusPresentWayCount['幫助判斷對方有空或沒空: 文字'] += item['selectedIsFreeA']
        contactStatusPresentWayCount['幫助判斷對方有空或沒空: 圖像'] += item['selectedIsFreeB']
        contactStatusPresentWayCount['幫助判斷對方有空或沒空: 數字'] += item['selectedIsFreeC']
        contactStatusPresentWayCount['想看到: 文字'] += item['selectedPreferWayA']
        contactStatusPresentWayCount['想看到: 圖像'] += item['selectedPreferWayB']
        contactStatusPresentWayCount['想看到: 數字'] += item['selectedPreferWayC']
    
    # for key, val in contactStatusPresentWayCount.items():
    #     print (key, ": ", val)

    return json.dumps(contactStatusPresentWayCount)    

if __name__ == '__main__':
    app.run(host="172.31.11.127")