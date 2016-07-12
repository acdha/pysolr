# encoding: utf-8

from __future__ import absolute_import, unicode_literals

import os
import subprocess
import time

# TODO: Add some mechanism so tools like Travis / Tox can specify multiple versions:
SOLR_TAG="solr:5"


def prepare():
    subprocess.check_call(['docker', 'pull', SOLR_TAG])

def start_solr():
    """Start a Solr container and return the URL for the running instance

    The current process environment will be updated to set TEST_SOLR_URL
    and TEST_SOLR_INSTANCE_ID for convenience
    """

    stdout = subprocess.check_output(['docker', 'run', '--detach', '--publish-all',
                                      '--label', 'pysolr-test-solr',
                                      SOLR_TAG],
                                     universal_newlines=True)
    instance_id = stdout.strip()
    os.environ['TEST_SOLR_INSTANCE_ID'] = instance_id

    random_port = subprocess.check_output(['docker', 'port', instance_id, '8983/tcp'],
                                          universal_newlines=True)

    os.environ['TEST_SOLR_URL'] = test_solr_url = 'http://%s/solr/' % random_port.strip()

    print('Waiting for test Solr instance %s on %s' % (instance_id, test_solr_url))

    for i in range(0, 60):
        try:
            subprocess.check_call(['docker', 'exec', '--user=solr', instance_id, 'bin/solr', 'status'])
            break
        except:
            time.sleep(1)

    subprocess.check_call(['docker', 'exec', '--user=solr', instance_id, 'bin/solr', 'create_core', '-c', 'core0'])

    return test_solr_url

def stop_solr():
    instance_id = os.environ['TEST_SOLR_INSTANCE_ID']
    subprocess.check_call(['docker', 'stop', instance_id])
    subprocess.check_call(['docker', 'rm', instance_id])

def get_solr_url():
    url = os.environ.get('TEST_SOLR_URL', 'http://localhost:8983/solr/')

    assert url.endswith('/')

    return url
