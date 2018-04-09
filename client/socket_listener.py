import sys

from json import loads
from threading import Thread
from json import JSONDecodeError

class SocketListener(Thread):
    def __init__(self, sock, buffer, queue):
        Thread.__init__(self)
        self.daemon = True
        self.socket = sock
        self.queue = queue
        self.buffer = buffer

    def run(self):
        while True:
            try:
                data = self.socket.recv(self.buffer).decode()
                messages = data.split('\0')
                for msg in messages[:-1]:
                    try:
                        data = loads(msg)
                        if data['type'] == 'end_game':
                            self.socket.close()
                    except JSONDecodeError as e:
                        print("JSONError: {0}\nmsg: {1}".format(e, msg), file=sys.stderr)

                    self.queue.put(msg)
            except (ConnectionResetError, OSError):
                exit(1)
