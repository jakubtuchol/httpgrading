import argparse
import subprocess
import requests
import time
import os


STATIC_RESOURCES = 'www'


class HttpTester(object):
    """
    List of expected objects
    """
    expected_resources = [
        'index.html',
        'foo/bar.html',
        'images/uchicago/logo.png',
    ]

    """
    List of expected redirects
    """
    expected_redirects = {
        'cats': 'http://en.wikipedia.org/wiki/Cat',
        'uchicago/cs': 'http://www.cs.uchicago.edu/',
    }

    """
    List of nonexistent paths
    """
    nonexistent_paths = [
        'stuff.html',
        'foo',
        'images/uchicago/log.png',
    ]

    def __init__(self, server_class, server_port):
        self.server_class = server_class
        self.server_port = server_port
        self.server_process = None
        self.http_host = 'http://localhost:{}'.format(server_port)

    def create_server(self):
        server_start_command = [
            'java',
            self.server_class,
            '--serverPort={}'.format(self.server_port),
        ]
        print('starting server with command')
        print(server_start_command)
        try:
            with open(os.devnull, 'w') as fp:
                self.server_process = subprocess.Popen(server_start_command, stdout=fp)
                print('Got server process')
                print(self.server_process.pid)
                time.sleep(0.5)
        except Exception as e:
            print('got exception when trying to open server process')
            print(e)

    def check_expected_resources(self):
        for resource in self.expected_resources:
            try:
                url_path = '{}/{}'.format(self.http_host, resource)
                res = requests.get(url_path)
                assert res.status_code == 200
            except IOError as e:
                print('Got io error in getting expected resources')
                print('Error: {}'.format(str(e)))
            except AssertionError:
                print('Got assertion error on path {} with expected status code {} and actual status code {}'.format(url_path, 200, res.status_code))

    def check_head_expected_resources(self):
        for resource in self.expected_resources:
            try:
                url_path = '{}/{}'.format(self.http_host, resource)
                res = requests.head(url_path)
                assert res.status_code == 200
                assert len(res.text) == 0
            except IOError as e:
                print('Got io error in getting expected resources')
                print('Error: {}'.format(str(e)))
            except AssertionError:
                print('Got assertion error on head path {} with expected status code {} and actual status code {} and expected len 0'.format(url_path, 200, res.status_code))

    def check_expected_redirects(self):
        for redirect in self.expected_redirects:
            try:
                url_path = '{}/{}'.format(self.http_host, redirect)
                res = requests.get(url_path, allow_redirects=False)
                assert res.status_code == 301
            except IOError as e:
                print('Got io error in redirect')
                print('Error: {}'.format(str(e)))
            except AssertionError:
                print('Got assertion error on path {} with expected status code {} and actual status code {}'.format(url_path, 301, res.status_code))

    def check_nonexistent_paths(self):
        for path in self.nonexistent_paths:
            try:
                url_path = '{}/{}'.format(self.http_host, path)
                res = requests.get(url_path)
                assert res.status_code == 404
                # assert len(res.text) == 0
            except IOError as e:
                print('Got exception when trying to get nonexistent path {}'.format(path))
                print(e)
            except AssertionError:
                print('Got assertion error on path {} with expected status code {} and actual status code {}'.format(url_path, 404, res.status_code))

    def check_nonallowed_methods(self):
        for path in self.expected_resources:
            try:
                url_path = '{}/{}'.format(self.http_host, path)
                res = requests.post(url_path, data = {'key':'value'})
                assert res.status_code == 403
            except IOError as e:
                print('Got exception when trying to handle non-allowed method on {}'.format(path))
                print(e)
            except AssertionError:
                print('Got assertion error on path {} with expected status code {} and actual status code {}'.format(url_path, 403, res.status_code))

    def check_head_works_same(self):
        for redirect in self.expected_redirects:
            try:
                url_path = '{}/{}'.format(self.http_host, redirect)
                res = requests.head(url_path, allow_redirects=False)
                assert res.status_code == 301
            except IOError as e:
                print('Got io error in redirect')
                print('Error: {}'.format(str(e)))
            except AssertionError:
                print(
                    'Got assertion error on path {} with expected status code {} and actual status code {}'.format(
                        url_path, 301, res.status_code
                    )
                )

        for path in self.nonexistent_paths:
            try:
                url_path = '{}/{}'.format(self.http_host, path)
                res = requests.head(url_path)
                assert res.status_code == 404
                assert len(res.text) == 0
            except IOError as e:
                print('Got exception when trying to get nonexistent path {}'.format(path))
                print(e)
            except AssertionError:
                print('Got assertion error on path {} with expected status code {} and actual status code {}'.format(url_path, 404, res.status_code))

    def check_multiple_connections(self):
        pass

    def destroy_server(self):
        self.server_process.kill()


parser = argparse.ArgumentParser()
parser.add_argument('--server-class', default='Server')
parser.add_argument('--server-port', default=8888)

args = parser.parse_args()

tester = HttpTester(
    args.server_class,
    args.server_port,
)
try:
    tester.create_server()
    tester.check_expected_resources()
    tester.check_expected_redirects()
    tester.check_nonexistent_paths()
    tester.check_nonallowed_methods()
    tester.check_head_works_same()
    print('server done')
finally:
    tester.destroy_server()
