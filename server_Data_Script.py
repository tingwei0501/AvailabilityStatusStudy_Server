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
    dumpDataCoount = collection.find({'id': user_id, 'createdTime': {'$gte': start.timestamp()*1000, '$lt': end.timestamp()*1000} }).count()
    
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

    # print (start.timestamp()*1000)
    # print (end.timestamp()*1000)
    # print (datetime.datetime(2019, 7, 5, 16, 0, 0).timestamp()*1000)
    # print (datetime.datetime(2019, 7, 6, 15, 59, 59).timestamp()*1000)

    collection = mongo.db.contactQuestionnaire
    dataSet = collection.find({'id': user_id, 'checkContactStatusTime': {'$gte': start.timestamp()*1000, '$lt': end.timestamp()*1000} })
    count = dict()
    for item in dataSet:
        print (item)
        # print (item['contactId'])
        if (item['contactId'] not in count):
            count[item['contactId']] = 1
        else:
            count[item['contactId']] += 1
    for key, value in count.items():
        print (key, " ", value)

    return json.dumps(count)


@app.route('/notificationCompletedRate', methods=['POST'])
def notificationCompletedRate():
    total = 0
    selfCompleted = 0
    selfEdit = 0

    jsonquery = request.get_json(force=True, silent=True)
    query = json.loads(jsonquery)
    user_id = query['id']
    start = datetime.datetime(2019, query['query_start_month'], query['query_start_date'], 0, 0, 0, 0)
    end = datetime.datetime(2019, query['query_end_month'], query['query_end_date']+1, 0, 0, 0, 0)

    # print (start.timestamp())
    # print (end.timestamp())

    collection = mongo.db.selfQuestionnaire
    totalQuestionnaires = collection.find({'id': user_id, 'createdTime': {'$gte': start.timestamp()*1000, '$lt': end.timestamp()*1000} })
    for item in totalQuestionnaires:
        if 'completeTime' not in item:
            total += 1
        else if 'completeTime' in item:
            timePeriodInSec = (item['completeTime'] - item['createdTime']) / 1000
            # <= 2 hours
            if timePeriodInSec <= 7200:
                if 'idealShowDifferent' in item:
                    selfCompleted += 1
                else:
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

if __name__ == '__main__':
    app.run(host="172.31.11.127")