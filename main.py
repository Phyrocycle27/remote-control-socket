import socket
import time

key = 'b3DL7F14d0XOYKxjz5yHchslAItZI0jE'
timeout = 30


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


client = socket.socket()

host = '192.168.1.71'
port = 3142

connect()

while True:
    msg = input(">")
    client.send(str.encode(msg, 'utf-8'))
    response = client.recv(1024)
    print(response.decode('utf-8'))
