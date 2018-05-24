from flask import Flask, jsonify, request, Response
from pymongo import MongoClient
import statistics

app = Flask(__name__)

# mdb_con_str = 'mongodb+srv://py-user:' + os.environ['mongo_db_pass'] + '@mongocluster-mitdf.mongodb.net/test'
mdb_con_str = 'mongodb://localhost/'
client = MongoClient(mdb_con_str)
mdb = client.config

# Get http://127.0.0.1:5000/config/dylan-xps
# Post http://127.0.0.1:5000/api/v1.0/keepalive/dylan-xps with EPOCH time in body
# Post http://127.0.0.1:5000/api/v1.0/send_monitor/dylan-xps with json monitor data in body
# Post http://127.0.0.1:5000/api/v1.0/get_monitor/dylan-xps with json {"query": ["http"]}
# Post http://127.0.0.1:5000/api/v1.0/get_monitor/dylan-xps/<operation> with json {"query": ["http","cpu"]}


@app.route('/config/<string:host_name>', methods=['GET'])
def get_config(host_name):
    host_config = mdb.systems.find_one({'_id': host_name})

    if not host_config:

        return Response('{"NotFound": true}', status=404,
                        mimetype='application/json')

    else:

        return jsonify(host_config)


@app.route('/api/v1.0/keepalive/<string:host_name>', methods=['POST'])
def send_keepalive(host_name):
    host_keepalive = mdb.keepalive.find_one({'_id': host_name})

    json_data = request.get_json()

    if 'epoch' in json_data:

        date = int(json_data['epoch'])

    else:

        return Response('{"BadData": true}', status=400,
                        mimetype='application/json')

    if not host_keepalive:

        json = {'_id': host_name, 'time': date}
        insert_result = mdb.keepalive.insert_one(json)
        return Response('{"Created": true}', status=201,
                        mimetype='application/json')
    else:

        host_keepalive['time'] = date
        update_result = mdb.keepalive.replace_one({'_id': host_name}, host_keepalive)
        return Response('{"Updated": true}', status=201,
                        mimetype='application/json')


@app.route('/api/v1.0/send_monitor/<string:host_name>', methods=['POST'])
def send_monitor(host_name):

    json = request.get_json()

    if not json:

        return Response('{"BadData": true}', status=400,
                        mimetype='application/json')

    temp_dict = {}

    for key, value in json.items():

        temp_dict[key] = {'$each': [value], '$slice': -60}

    update_result = mdb.monitor.update_one({'_id': host_name}, {'$push': temp_dict}, upsert=True)

    return Response('{"Updated": true}', status=201,
                    mimetype='application/json')


@app.route('/api/v1.0/get_monitor/<string:host_name>', methods=['POST'])
def get_monitor(host_name):
    json = request.get_json()

    if 'query' in json:

        search_query = {'_id': host_name}
        projection = {}

        for k in json['query']:
            projection[k] = 1

        data = mdb.monitor.find_one(search_query, projection)

        return jsonify(data)

    else:

        return Response('{"BadData": true}', status=400,
                        mimetype='application/json')


@app.route('/api/v1.0/get_monitor/<string:host_name>/<string:operation>', methods=['POST'])
def math_monitor(host_name, operation):
    json = request.get_json()
    if 'query' in json:

        search_query = {'_id': host_name}
        projection = {'_id': 0}

        for k in json['query']:
            projection[k] = 1

        data = mdb.monitor.find_one(search_query, projection)

        temp_dict = {}

        for key, value in data.items():

            if operation.lower() == 'average':

                temp_dict[key] = sum(value) / len(value)

            elif operation.lower() == 'max':

                temp_dict[key] = max(value)

            elif operation.lower() == 'min':

                temp_dict[key] = min(value)

            elif operation.lower() == 'median':

                temp_dict[key] = statistics.median(value)

            else:

                return Response('{"Invalid math operation. Please use average, max, min, or median.": true}', status=400,
                                mimetype='application/json')

        return jsonify(temp_dict)

    else:

        return Response('{"BadData": true}', status=400,
                        mimetype='application/json')


if __name__ == '__main__':
    app.run()
