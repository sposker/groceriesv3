#! python3
"""Host script for database, pools, lists, etc."""

import datetime
import os
import socket
import threading
from http import server, HTTPStatus


class MyHandler(server.SimpleHTTPRequestHandler):
    allowed_ips = ['127.0.0.1',
                   '192.168.1.154',
                   '192.168.1.241',
                   '192.168.1.242',
                   '192.168.1.252'
                   ]

    def handle_one_request(self):
        print(self.client_address[0], self.client_address)
        if str(self.client_address[0]) in MyHandler.allowed_ips:
            return server.SimpleHTTPRequestHandler.handle_one_request(self)

    def handle(self):
        print(self.client_address[0], self.client_address)
        if str(self.client_address[0]) in MyHandler.allowed_ips:
            return server.SimpleHTTPRequestHandler.handle(self)
        else:
            return HTTPStatus.FORBIDDEN


def get_date(length):
    date, dtime = str(datetime.datetime.now()).split(" ")
    y, m, d = date.split('-')
    hour, minute, _ = dtime.split(':')
    if length == 5:
        return f'{y}.{m}.{d}.{hour}.{minute}.'
    else:  # length == 3
        return f'{y}.{m}.{d}.'


def listen_to_connection(s):
    c, addr = s.accept()
    # print('Got connection from ', addr)

    message = ''
    incoming = c.recv(1024)

    while incoming:
        message += incoming.decode()
        incoming = c.recv(1024)

    return message


def _serve(_):
    handler = MyHandler
    address = ('', 42209)
    myserver = server.HTTPServer(address, handler)
    myserver.serve_forever()


def _write(_):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 42210
    s.bind(('0.0.0.0', port))
    s.listen(3)

    while True:
        message = listen_to_connection(s)
        relative_path, body = message.split('::')
        filepath = os.path.join(os.getcwd(), relative_path)
        with open(filepath, 'w') as f:
            f.write(body)


def _rename_database(_):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 42211
    s.bind(('0.0.0.0', port))
    s.listen(3)

    while True:
        message = listen_to_connection(s)
        current, new_name = message.split('::')
        os.rename(current, new_name)


def main():
    x, y, z = (threading.Thread(target=_serve, args=(1,)),
               threading.Thread(target=_write, args=(1,)),
               threading.Thread(target=_rename_database, args=(1,)),
               )
    for thread in [x, y, z]:
        thread.start()


if __name__ == "__main__":
    main()
