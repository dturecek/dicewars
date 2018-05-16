import sys
import logging

from json import loads
from threading import Thread
from json import JSONDecodeError


class SocketListener(Thread):
    """Daemon for collecting messages from the server
    """
    def __init__(self, sock, buffer, queue):
        """
        Parameters
        ----------
        sock : socket
        buffer : int
        queue : Queue
            Queue of incoming messages
        """
        Thread.__init__(self)
        self.logger = logging.getLogger('SOCKET')

        self.socket = sock
        self.queue = queue
        self.buffer = buffer

    def run(self):
        """Collect messages from the server
        """
        buffer = ''
        while True:
            try:
                data = self.socket.recv(self.buffer).decode()
                messages = data.split('\0')
                for msg in messages:
                    if not msg:
                        continue
                    buffer += msg
                    try:
                        data = loads(buffer)
                        if data['type'] == 'end_game':
                            self.socket.close()
                        self.queue.put(data)
                        buffer = ''
                    except JSONDecodeError as e:
                        self.logger.warning("buffer: {0}\nmsg: {1}\nJSONDecodeError: {2}".format(buffer, msg, e))
                        self.logger.warning("JSONDecodeError: {0}\nmsg: {1}".format(e, msg))
                    except JSONError as e:
                        self.logger.warning("buffer: {0}\nmsg: {1}".format(buffer, msg, e))
                        self.logger.warning("JSONError: {0}\nmsg: {1}\nJSONError: {2}".format(e, msg))

            except (ConnectionResetError, OSError):
                exit(1)
