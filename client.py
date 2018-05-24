import requests
import os
import json
import platform
import time
import psutil
import sys

cwd = os.getcwd()
node_name = platform.node()
file_path = cwd + '/config.json'

with open(file_path) as file:
    data = json.load(file)

base_uri = 'http://' + data['host'] + ':' + data['port']


def get_current_config():
    config_uri = base_uri + '/config/' + node_name
    try:
        config = requests.get(config_uri)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    json_config = json.loads(config.text)

    if not platform.node() == json_config['_id']:
        raise Exception("Node names do not match!")

    return json_config


def send_monitor_data(uri, js):
    try:
        result = requests.post(uri, json=js)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    return result


while True:
    host_config = get_current_config()
    epoch = str(int(time.time()))

    keepalive_uri = base_uri + '/api/v1.0/keepalive/' + node_name
    keepalive = requests.post(keepalive_uri, data=epoch)

    if host_config['http']:
        test_result = requests.get('https://google.com')
        json_data = {"http": test_result.elapsed.total_seconds()}

        monitor_uri = base_uri + '/api/v1.0/monitor/' + node_name
        monitor_result = requests.post(monitor_uri, json=json_data)

    if host_config['cpu']:
        json_data = {"cpu": psutil.cpu_percent()}

        monitor_uri = base_uri + '/api/v1.0/monitor/' + node_name
        monitor_result = requests.post(monitor_uri, json=json_data)

    if host_config['mem']:
        mem_data = psutil.virtual_memory()
        json_data = {"mem_free": mem_data.free, "mem_total": mem_data.total, "mem_cached": mem_data.cached,
                     "mem_used": mem_data.used}

        monitor_uri = base_uri + '/api/v1.0/monitor/' + node_name
        monitor_result = requests.post(monitor_uri, json=json_data)

    print("Sleeping for 10 seconds")
    time.sleep(10)
