#! python3
"""Host script for database, pools, lists, etc."""


import datetime
import os
from http import server, HTTPStatus
import threading
import socket


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


def interpret_and_dump(c, filename):
    list_text = ''
    incoming = c.recv(1024)

    while incoming:
        list_text += incoming.decode()
        incoming = c.recv(1024)

    c.close()
    with open(filename, 'w') as f:
        f.write(list_text)


def get_date(length):
    date, dtime = str(datetime.datetime.now()).split(" ")
    y, m, d = date.split('-')
    hour, minute, _ = dtime.split(':')
    if length == 5:
        return f'{y}.{m}.{d}.{hour}.{minute}.'
    else:  # length == 3
        return f'{y}.{m}.{d}.'


def _serve(_):
    handler = MyHandler
    address = ('', 42209)
    myserver = server.HTTPServer(address, handler)
    myserver.serve_forever()


def _list_text(_):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 42210
    s.bind(('0.0.0.0', port))
    s.listen(3)

    while True:
        c, addr = s.accept()
        print('Got connection from ', addr)

        directory = os.path.join(os.getcwd(), 'username/lists/')
        base = 'ShoppingList.txt'

        filename = os.path.join(directory, get_date(3) + base)

        interpret_and_dump(c, filename)


def _yaml_db(_):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 42211
    s.bind(('0.0.0.0', port))
    s.listen(3)

    while True:
        c, addr = s.accept()
        print('Got connection from ', addr)

        root = os.getcwd()
        path = os.path.join(root, 'username/old_database')
        db_path = os.path.join(root, 'username/username.yaml')
        new_filename = os.path.join(get_date(5) + 'username.yaml')
        new_filepath = os.path.join(path, new_filename)
        os.rename(db_path, new_filepath)

        interpret_and_dump(c, db_path)


def main():
    x, y, z = threading.Thread(target=_serve, args=(1,)), \
              threading.Thread(target=_yaml_db, args=(1,)), \
              threading.Thread(target=_list_text, args=(1,))
    for thread in [x, y, z]:
        thread.start()


if __name__ == "__main__":
    main()
