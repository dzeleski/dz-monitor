import requests, os, json, platform, time, psutil


cwd = os.getcwd()
node_name = platform.node()

file_path = cwd + '/config.json'

with open(file_path) as file:
    data = json.load(file)

base_uri = 'http://' + data['host'] + ':' + data['port']

config_uri = base_uri + '/config/' + node_name
config = requests.get(config_uri)
json_config = json.loads(config.text)

if not platform.node() == json_config['_id']:
    raise Exception("Node names do not match!")


while True:
    epoch = str(int(time.time()))

    keepalive_uri = base_uri + '/api/v1.0/keepalive/' + node_name
    keepalive = requests.post(keepalive_uri, data=epoch)

    if json_config['http']:
        test_result = requests.get('https://google.com')
        json = {"http": test_result.elapsed.total_seconds()}

        monitor_uri = base_uri + '/api/v1.0/monitor/' + node_name
        monitor_result = requests.post(monitor_uri, json=json)

    if json_config['cpu']:
        json = {"cpu": psutil.cpu_percent()}

        monitor_uri = base_uri + '/api/v1.0/monitor/' + node_name
        monitor_result = requests.post(monitor_uri, json=json)

    if json_config['mem']:
        mem_data = psutil.virtual_memory()
        json = {"mem_free": mem_data.free, "mem_total": mem_data.total, "mem_cached": mem_data.cached
                , "mem_used": mem_data.used}

        monitor_uri = base_uri + '/api/v1.0/monitor/' + node_name
        monitor_result = requests.post(monitor_uri, json=json)

    print("Sleeping for 10 seconds")
    time.sleep(10)
