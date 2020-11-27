import os
import atexit
from requests import get, post, exceptions
from flask import Flask, request

app = Flask(__name__)


steamVR_gameid = '250820'
FFX_gameid = '359870'
launch_cmd = 'start steam://rungameid/{0}'
register_url = 'http://172.16.0.147:5000/register'


# Register to manager
def register_server():
    try:
        r = get(register_url)
    except exceptions.RequestException as e:
        raise SystemExit(e)


register_server()


@app.route('/')
def index():
    print('host', request.host.split(':')[0])
    print('remote_addr', request.remote_addr)
    return 'CloudXR server'


@app.route('/connection')
def launch_cloudxr():
    connection_type = request.args.get('type', type=str)
    client_ip = request.remote_addr
    print(client_ip)
    game_server_ip = '0.0.0.0'
    if connection_type == 'gaming':
        if os.system(launch_cmd.format(steamVR_gameid)) == 0:
            return {'launch success': True,
                    'command': 'CloudXRClient.exe -s {0}'.format(game_server_ip)}
        else:
            return {'launch success': False}
    elif connection_type == 'streaming':
        return 'streaming'
    else:
        return 'Please specify the connection type.'


def terminate_connection():
    res = get('http://172.16.0.147:5000/disconnection')
    print(res.text)


atexit.register(terminate_connection)
if __name__ == '__main__':
    app.run()