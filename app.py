import os
import atexit
from requests import get, post, exceptions
from flask import Flask, request

app = Flask(__name__)


steamVR_gameid = '250820'
hellblade = '747350'
launch_cmd = 'start steam://rungameid/{0}'
close_cmd = 'taskkill /IM "{0}" /F'
# game_server_manager_ip = '172.16.0.147'
game_server_manager_ip = '192.168.0.108'
is_available = 1
player_ip = ''


# Register to manager
def register_server():
    try:
        r = get('http://{0}:5000/registration'.format(game_server_manager_ip))
    except exceptions.RequestException as e:
        raise SystemExit(e)


def unregistered():
    res = get('http://{0}:5000/cancellation'.format(game_server_manager_ip))
    print(res.text)


register_server()
atexit.register(unregistered)


@app.route('/')
def index():
    print('host', request.host.split(':')[0])
    print('remote_addr', request.remote_addr)
    return 'CloudXR server'


@app.route('/game-connection', methods=['POST'])
def launch_cloudxr():
    global player_ip, is_available
    if not is_available:
        return 'Game server not available now'
    game_title = request.form.get('game_title', type=str)
    game_id = request.form.get('game_id', type=str)
    player_ip = request.form.get('player_ip', type=str)
    print(game_title, game_id, player_ip)
    # Game_id needs to be generalized
    if os.system(launch_cmd.format(steamVR_gameid)) == 0:
    # if os.system(launch_cmd.format(hellblade)) == 0:
        is_available = 0
        print('Available: ', is_available)
        return {'launch success': True}
    else:
        return {'launch success': False}


@app.route('/game-disconnection', methods=['POST'])
def close_clourdxr():
    global player_ip, is_available
    print(player_ip, request.remote_addr)
    if request.remote_addr != player_ip and player_ip != '127.0.0.1':
        return 'Invalid request'
    # Close game app and steamVR, and reset game server status
    if os.system(close_cmd.format("vrmonitor.exe")) == 0:
        player_ip = ''
        is_available = 1
        print(player_ip, is_available)
        register_server()
        return {'close success': True}
    else:
        return {'close success': False}


@app.route('/stream-info')
def get_stream_info():
    return 'Under construction'


if __name__ == '__main__':
    app.run()
