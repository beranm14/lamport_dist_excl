import json
import socket
import sys
import signal
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
hdlr = logging.FileHandler('./log/var_simulator.log')
formatter = logging.Formatter(
    '%(asctime)s %(levelname)s %(process)d %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)


def signal_handler(signal, frame):
    s.close()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


class lamport_communication:
    """Lamport communication helper, it provides interface
        for communication releated things.

    Attributes:
        nodes (:obj:`list` of :obj:`str`):
            list of nodes in topology..
        source_ip (str): Source ip of node (it does not
            need to be only ip, socket.connect manages
            even hostnames).
        whoami (str): Name of node.
        socket_ (:obj:`socket`) Socket to bind on local port
            to listen for other senders.

    """

    nodes_ = []
    source_ip = ""
    source_po = 0
    whoami = ""
    socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self, nodes, whoami):
        """Construct Lamport communication object.

        Binds sockets and prepare whole communication. Also
        is able to create requests and send them through
        independent sockets.

        Args:
            whoami (str): Which node in nodes is this.
            nodes (:obj:`list` of :obj:`str`): List of nodes.
        """
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

    def get_targets(self, i):
        """Helper function to parse target and port of target

        Args:
            i (str): String with target:port.

        Returns:
            Touple of target and port of target.
        """
        return (i.split(":")[0], int(i.split(":")[1]))

    def send_request(self, ip, port, message):
        """Sends only messages with flag request.

        Args:
            ip (str): String stateing target, it does not need
                need to be only ip, socket.connect is not stupid.
            port (int): Port of target.
            message (str): String containing message.

        """
        logger.debug(
            "Sending request " + ip + ":" + str(port) + " " + str(message))
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

    def send_request_nd(self, node, message):
        """Sends only messages with flag request.

        Args:
            ip (str): String stateing target, it does not need
                need to be only ip, socket.connect is not stupid.
            port (int): Port of target.
            message (str): String containing message.

        """
        (ip, port) = self.get_targets(node)
        logger.debug(
            "Sending request " + ip + ":" + str(port) + " " + str(message))
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
        """Sends only messages with flag response.

        Args:
            ip (str): String stateing target, it does not need
                need to be only ip, socket.connect is not stupid.
            port (int): Port of target.
            message (str): String containing message.

        """
        logger.debug(
            "Sending response " + ip + ":" + str(port) + " " + str(message))
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
        """Sends only messages with flag release.

        Args:
            ip (str): String stateing target, it does not need
                need to be only ip, socket.connect is not stupid.
            port (int): Port of target.
            message (str): String containing message.

        """
        logger.debug(
            "Sending release " + ip + ":" + str(port) + " " + str(message))
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
        """Sends only messages with flag end.

        Args:
            ip (str): String stateing target, it does not need
                need to be only ip, socket.connect is not stupid.
            port (int): Port of target.
            message (str): String containing message.

        """
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

    def send_var(self, ip, port, message):
        """Sends only messages with flag var and with message as var.

        Args:
            ip (str): String stateing target, it does not need
                need to be only ip, socket.connect is not stupid.
            port (int): Port of target.
            message (str): String containing message.

        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        s.send(
            bytes(
                json.dumps(
                    {
                        'type': 'var',
                        'message': message,
                        'source': self.whoami
                    }
                ) + '\0', 'UTF-8')
        )
        s.close()

    def broadcast_var(self, message):
        """Sends only messages with flag var to all the other nodes.

        Args:
            message (str): String containing message.

        """
        failed_nodes = []
        for i in self.nodes_:
            (target_ip, target_po) = self.get_targets(i)
            try:
                self.send_var(target_ip, target_po, message)
            except socket.error:
                logging.debug("Failed node " + str(i))
                failed_nodes.append(i)
        return failed_nodes

    def broadcast_request(self, message):
        """Sends only messages with flag request to all the other nodes.

        Args:
            message (str): String containing message.

        """
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
        """Sends only messages with flag release to all the other nodes.

        Args:
            message (str): String containing message.

        """
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
        """Helper function which listens on the upcomming
            messages and pass them into listener.

        """
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
