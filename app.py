from flask import Flask, jsonify, request, Response
import datetime, os
from pymongo import MongoClient

app = Flask(__name__)

mdb_con_str = 'mongodb+srv://py-user:' + os.environ['mongo_db_pass'] + '@mongocluster-mitdf.mongodb.net/test'
client = MongoClient(mdb_con_str)
mdb = client.config

filePath = '/home/dylan/Desktop/data.txt'


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

    try:
        date = int(request.data.decode("utf-8"))
    except ValueError:
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


@app.route('/api/v1.0/send', methods=['POST'])
def send_data():
    date = datetime.datetime.now().strftime("%y-%m-%d-%H-%M-%s")
    file = open(filePath, 'a')
    data = request.data.decode("utf-8")
    file.write(date + ',' + data + '\n')
    file.close()
    return Response('{"Success": true}', status=201,
                    mimetype='application/json')


if __name__ == '__main__':
    app.run()
