from iron_worker import *
import json
import requests
import yaml

payload_file = None
payload = None
runner_payload = None

with open('iron.json', 'r') as f:
    credentials = json.loads(f.read())

with open('config.yml', 'r') as f:
    config = yaml.load(f.read())

r = requests.post('{0}/api/v1/builds/register'.format(config['ci']['url']),
                  verify=False,
                  data=config['runner'])


resp = json.loads(r.text)

if 'id' in resp.keys():
    '''
    Create a worker
    '''
    print "found job..."

    worker = IronWorker(project_id=credentials['project_id'],
                        token=credentials['token'])

    task = Task(code_name="runner")
    task.payload = resp
    response = worker.queue(task)
    print "job queued..."
else:
    print "no builds scheduled..."
