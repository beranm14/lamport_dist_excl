from .lamport_timer import lamport_timer
from .lamport_communication_var import lamport_communication
from threading import Thread
from queue import Queue
import yaml
import logging

# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger(__name__)
# logger.propagate = False

receive_ansv_ = False
request_queue_ = []
failed_nodes = []
end_flag = False
shared_var = ""


class lamport_var:

    nodes_ = []

    def __init__(self, whoami, path_to_nodes='./lamport/nodes.yml'):
        with open(path_to_nodes, 'r') as stream:
            logger.debug("Reading nodes")
            for i in yaml.load(stream)['nodes']:
                if i != whoami:
                    self.nodes_.append(i)
            logger.debug("Nodes " + str(self.nodes_))
        self.timer_ = lamport_timer(whoami)
        self.comm_ = lamport_communication(
            self.nodes_, whoami)
        self.whoami = whoami
        logger.debug("Whoami " + str(whoami))
        logger.debug("Timer " + str(self.timer_.timer_))
        self.start_listen()

    def publish(self, message):
        global request_queue_, failed_nodes
        self.timer_.timer_incr()
        logger.info("Local publish requested")
        logger.debug("Local timer: %d", self.timer_.timer_)
        request = [self.whoami, self.timer_.timer_, message]
        request_queue_.append(request)
        logger.debug("Request " + str(request))
        failed_nodes = self.comm_.broadcast_request(request)
        winner_request = self.test_winner()
        return winner_request[2]  # returning just a variable

    def read_var(self):
        global request_queue_, failed_nodes
        request_queue_.sort(key=lambda x: x[1])
        if len(request_queue_) == 0:
            return ""
        # tail is the biggest timestamp
        tail = request_queue_[-1]
        # if there is somebody with the same timestamp, sort by ID
        times_ = list(
            filter(
                lambda x: x[1] == tail[1],
                request_queue_
            )
        )
        times_.sort(key=lambda x: x[0])
        logging.debug("sorted_hosts_ " + str(times_))
        return times_[-1][2]

    def all_node_sent(self, cmp_nodes):
        logger.debug(
            "Comparing " +
            str(sorted(self.nodes_)) + " " +
            str(sorted(cmp_nodes)) + " " +
            str(sorted(self.nodes_) == sorted(cmp_nodes)))
        return sorted(self.nodes_) == sorted(cmp_nodes)

    def start_listen(self):
        self.queue_ = Queue()
        self.listener = Thread(target=self.listener)
        self.listener.start()

    def test_winner(self):
        global request_queue_, failed_nodes
        # if request[1] in [k[1] for k in request_queue_]:
        #     raise ValueError("Lock with same timestamp already taken!")
        # request_queue_.append(request)
        logger.debug("Switching to wait for request state")
        ans_nodes = []
        # check if nodes are not already offline
        if not self.all_node_sent(failed_nodes):
            # add offline nodes to the ansvered nodes
            ans_nodes = failed_nodes
            while 1:
                # wait for all nodes to ansver
                message = self.queue_.get(True)
                logger.debug("Got message " + str(message['message']))
                ans_nodes.append(message['source'])
                if message['message'] not in request_queue_:
                    request_queue_.append(message['message'])
                if self.all_node_sent(ans_nodes):
                    break
        # pick message with the biggest timestamp
        request_queue_.sort(key=lambda x: x[1])
        if len(request_queue_) == 0:
            raise ValueError("Nobody responsed!")
        # tail is the biggest timestamp
        tail = request_queue_[-1]
        self.timer_.timer_ = tail[1]
        # if there is somebody with the same timestamp, sort by ID
        times_ = list(
            filter(
                lambda x: x[1] == tail[1],
                request_queue_
            )
        )
        times_.sort(key=lambda x: x[0])
        logging.debug("sorted_hosts_ " + str(times_))
        return times_[-1]

    def listener(self):
        global request_queue_, end_flag, shared_var
        while 1:
            message = self.comm_.receive_()
            logger.debug('Received message: ' + str(message))
            if message['type'] == 'end' and message['source'] == self.whoami:
                return
            elif message['type'] == 'response':
                self.queue_.put(message)
            elif message['type'] == 'request':
                logger.debug('request_queue_ ' + str(request_queue_))
                request_queue_.append(message['message'])
                request_queue_.sort(key=lambda x: x[1])
                tail = request_queue_[-1]
                self.timer_.timer_ = tail[1]
                times_ = list(
                    filter(
                        lambda x: x[1] == tail[1],
                        request_queue_
                    )
                )
                times_.sort(key=lambda x: x[0])
                tail = times_[-1]
                logger.debug('tail value ' + str(tail))
                (ip, port) = self.comm_.get_targets(message['source'])
                self.comm_.send_response(ip, port, tail)
            else:
                logger.info('This was not covered ' + str(message))
            if end_flag:
                return

    def finnish(self):
        global end_flag
        end_flag = True
        (ip, port) = self.comm_.get_targets(self.whoami)
        self.comm_.send_end(ip, port)
