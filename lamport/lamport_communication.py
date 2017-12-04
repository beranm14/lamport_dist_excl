import json
import socket
import sys
import signal
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def signal_handler(signal, frame):
    s.close()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


class lamport_communication:

    nodes_ = []
    source_ip = ""
    source_po = 0
    whoami = ""
    socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def get_targets(self, i):
        # logger.debug('get_targets ' + str(i))
        return (i.split(":")[0], int(i.split(":")[1]))

    def __init__(self, nodes, whoami):
        global s
        global receive_ansv_
        receive_ansv_ = False
        s = self.socket_
        self.whoami = whoami
        self.nodes_ = nodes

        logger.debug("Binding socket " + str(whoami))
        (source_ip, source_po) = self.get_targets(whoami)
        self.socket_.bind((source_ip, source_po))
        self.socket_.listen(1)

    def send_request(self, ip, port, message):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        s.send(
            bytes(
                json.dumps(
                    {
                        'type': 'request',
                        'message': message,
                        'source': self.whoami
                    }
                ) + '\0', 'UTF-8')
        )
        s.close()

    def send_response(self, ip, port, message):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        s.send(
            bytes(
                json.dumps(
                    {
                        'type': 'response',
                        'message': message,
                        'source': self.whoami
                    }
                ) + '\0', 'UTF-8')
        )
        s.close()

    def send_release(self, ip, port, message):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        s.send(
            bytes(
                json.dumps(
                    {
                        'type': 'release',
                        'message': message,
                        'source': self.whoami
                    }
                ) + '\0', 'UTF-8')
        )
        s.close()

    def send_end(self, ip, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        s.send(
            bytes(
                json.dumps(
                    {
                        'type': 'end',
                        'message': 'end',
                        'source': self.whoami
                    }
                ) + '\0', 'UTF-8')
        )
        s.close()

    def broadcast_request(self, message):
        failed_nodes = []
        for i in self.nodes_:
            (target_ip, target_po) = self.get_targets(i)
            try:
                self.send_request(target_ip, target_po, message)
            except socket.error:
                logging.debug("Failed node " + str(i))
                failed_nodes.append(i)
        return failed_nodes

    def broadcast_release(self, message):
        logging.debug("Broadcast release " + str(message))
        failed_nodes = []
        for i in self.nodes_:
            (target_ip, target_po) = self.get_targets(i)
            try:
                self.send_release(target_ip, target_po, message)
            except socket.error:
                logging.debug("Failed node " + str(i))
                failed_nodes.append(i)
        return failed_nodes

    def receive_(self):
        BUFFER_SIZE = 512
        data = b''
        conn, addr = self.socket_.accept()
        logging.debug("Received from " + str(addr))
        while 1:
            new_data = conn.recv(BUFFER_SIZE)
            data = data + new_data
            if new_data[-1:] == b'\x00':
                break
        message = json.loads(data[:-1].decode("utf-8"))
        logging.debug("Received message " + str(message))
        return message
