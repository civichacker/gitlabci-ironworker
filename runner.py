import requests
import json
import time
import pexpect
from git import Repo
import os
import sys
import yaml


payload_file = None
payload = None
repo_url = None
repo = None
ci_payload = None

os.environ['PATH'] = '/task/.local/bin:' + os.environ['PATH']


def run_commands(commands):
    out = None
    status = None
    try:
        (out, status) = pexpect.run(commands,
                                    withexitstatus=1,
                                    cwd='dir')
    except Exception as e:
        out = e
        status = -1
    return (out, status)


def update_status(_id, status, trace=None):
    ci_payload['runner']['state'] = status
    if trace is not None:
        ci_payload['runner']['trace'] = trace
    requests.put('{0}/api/v1/builds/{1}'.format(ci_payload['ci']['url'], _id),
                 verify=False,
                 data=ci_payload['runner'])

for i in range(len(sys.argv)):
    if sys.argv[i] == "-payload" and (i + 1) < len(sys.argv):
        payload_file = sys.argv[i + 1]
        with open(payload_file, 'r') as f:
            payload = json.loads(f.read())
        break


with open("config.yml", 'r') as f:
    ci_payload = yaml.load(f.read())

'''
Check if the needful are defined
then clone, reset and run something.
'''
repo_url = payload['repo_url']
commit_hash = payload['sha']
branch = payload['ref']

if repo_url is not None and commit_hash is not None:
    try:
        repo = Repo.clone_from(repo_url, 'dir')
        repo.head.reset(commit=commit_hash,
                        index=True,
                        working_tree=True)

        '''
        Parse commands
        '''

        stat = 'running'
        trace = ''
        for command in payload['commands'].split("\r\n"):
            time.sleep(10)
            (t, code) = run_commands(command)
            trace = trace+t
            if code is -1:
                stat = 'failed'
                break
            elif code is 0 or code is None:
                stat = 'success'
            else:
                stat = 'failed'
                break
        print "trace: "+trace
        print "status: "+stat
        update_status(payload['id'], stat, trace)
    except Exception as e:
        update_status(payload['id'],
                      'failed',
                      'failed to execute job')

else:
    print "This is going to fail"  # probably send an email or text
    update_status(payload['id'], 'failed', 'unsuccessful clone')
