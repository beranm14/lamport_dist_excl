from .lamport_timer import lamport_timer
from .lamport_communication import lamport_communication
from threading import Thread
from queue import Queue
import yaml
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

receive_ansv_ = False
request_queue_ = []


class lamport:

    timer_ = lamport_timer()
    nodes_ = []

    def __init__(self, whoami, path_to_nodes='./lamport/nodes.yml'):
        print(path_to_nodes)
        with open(path_to_nodes, 'r') as stream:
            logger.debug("Reading nodes")
            self.nodes_ = [
                (i if i != whoami else i) for i in yaml.load(stream)['nodes']]
            logger.debug("Nodes " + str(self.nodes_))
        self.comm_ = lamport_communication(
            self.nodes_, whoami)
        self.whoami = whoami
        self.start_listen()

    def lock(self):
        global request_queue_
        logger.info("Local lock requested")
        logger.debug("Local timer: %d", self.timer_.timer_)
        request = [self.whoami, self.timer_.timer_]
        request_queue_.append(request)
        logger.debug("Request " + str(request))
        self.comm_.broadcast_request(request)
        if self.test_winner(request):
            self.timer_.timer_incr()
            return True
        return False

    def unlock(self):
        global request_queue_
        logger.info("Unlock requested")
        request = [self.whoami, self.timer_.timer_]
        logger.debug("Request " + str(request))
        self.comm_.broadcast_release(request)
        request_queue_.remove(request)
        return True

    def all_node_sent(self, cmp_nodes):
        tmp = cmp_nodes
        print(tmp)
        for i in self.nodes_:
            tmp.remove(i)
        if len(tmp) == 0:
            return True
        return False

    def start_listen(self):
        self.queue_ = Queue()
        self.listener = Thread(target=self.listener)
        self.listener.start()

    def test_winner(self, request):
        global receive_ansv_, request_queue_
        receive_ansv_ = True
        ans_nodes = []
        while 1:
            message = self.queue_.get(True)  # add timeout
            ans_nodes.append(message[1])
            request_queue_.append(message)
            if self.all_node_sent(ans_nodes):
                break
        request_queue_.sort(key=lambda x: x[0])
        tail = request_queue_[-1:][0]
        if tail == request:
            return True
        return False

    def listener(self):
        global receive_ansv_, request_queue_
        message = self.comm_.receive_()
        logger.debug('Received message: ' + str(message))
        if receive_ansv_ is True and message['type'] == 'request':
            self.queue_.put(message['message'])
        elif receive_ansv_ is False and message['type'] == 'request':
            request_queue_.append(message['message'])
            logger.debug('request_queue_ ' + str(request_queue_))
            request_queue_.sort(key=lambda x: x[0])
            tail = request_queue_[-1:][0]
            (ip, port) = self.comm_.get_targets(tail[1])
            self.comm_.send_request(ip, port, tail)
        elif receive_ansv_ is False and message['type'] == 'release':
            request_queue_.remove(message['message'])
