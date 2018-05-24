import requests
from pymongo import MongoClient
import time
import os

api_key = os.environ['push_over_apikey']
user_key = os.environ['push_over_userkey']

mdb_con_str = 'mongodb://localhost/'
client = MongoClient(mdb_con_str)
mdb = client.config


def send_notification(msg):

    r = requests.post("https://api.pushover.net/1/messages.json", data={
      "token": api_key,
      "user": user_key,
      "message": msg
    })
    return r


all_hosts = mdb.systems.find()

for host in all_hosts:

    host_keepalive = mdb.keepalive.find_one({'_id': host['_id']})
    host_last_keepalive = host_keepalive['time']
    now = int(time.time())

    dif = now - host_last_keepalive

    if dif > 300:

        send_msg = "WARNING: " + host['_id'] + " has not reported within the last 5 min!"

        send_notification(send_msg)
        print(send_msg)

    for key, value in host.items():

        if not key == 'thresholds' and not key == '_id' and value:

            search_query = {'_id': host['_id']}
            projection = {key: 1, '_id': 0}

            data = mdb.monitor.find_one(search_query, projection)
            threshold = host['thresholds'][key]
            metric = sum(data[key]) / len(data[key])

            if metric > threshold:
                send_msg = "WARNING: " + host['_id'] + ": " + key + " is above: " + str(threshold) + " Value: " +\
                           str(metric)

                send_notification(send_msg)
                print(send_msg)


