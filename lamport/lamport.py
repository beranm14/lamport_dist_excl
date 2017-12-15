from .lamport_timer import lamport_timer
from .lamport_communication import lamport_communication
from threading import Thread
from queue import Queue
import queue
import yaml
import logging
import socket

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
hdlr = logging.FileHandler('./log/var_simulator.log')
formatter = logging.Formatter(
    '%(asctime)s %(levelname)s %(process)d %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)


receive_ansv_ = False
request_queue_ = []
failed_nodes = []
end_flag = False
shared_var = ""


class lamport:
    """Obtain lock in sense of Lamport algorithm.

    Attributes:
        nodes (:obj:`list` of :obj:`str`):
            list of nodes in topology..

    """

    nodes_ = []
    lock_ = []

    def __init__(self, whoami, path_to_nodes='./lamport/nodes.yml'):
        """Construct Lamport variable object, read nodes from yaml.

        Also prepare connection to the other nodes.

        Args:
            whoami (str): Which node in nodes is this.
            path_to_nodes (str): Path to yam with other
                nodes description.
        """
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

    def lock(self):
        """Create a lock in topology

        Returns:
            True if lock was taken by node.

        """
        global request_queue_, failed_nodes
        logger.info("Local lock requested")
        logger.debug("Local timer: %d", self.timer_.timer_)
        request = [self.whoami, self.timer_.timer_]
        request_queue_.append(request)
        logger.debug("Request " + str(request))
        self.timer_.timer_incr()
        # failed_nodes = self.comm_.broadcast_request(request)
        # this is removed and unicast were used
        if self.test_winner(request):
            self.lock_ = request
            logger.debug("Lock taken")
            return True
        logger.debug("Lock already taken")
        self.comm_.broadcast_release(request)
        request_queue_.remove(request)
        logger.debug("Requested for lock removal")
        self.lock_ = []
        return False

    def unlock(self):
        """Send unlock in topology, that actually removes message in
            all the queues in topology.

        Returns:
            True if lock was taken by node.

        """
        global request_queue_
        if self.lock_ == []:
            raise ValueError("Lock is empty!")
        logger.info("Unlock requested")
        logger.debug("Request " + str(self.lock_))
        self.comm_.broadcast_release(self.lock_)
        logging.debug(
            "Removing from list " +
            str(request_queue_) +
            " request " + str(self.lock_))
        request_queue_.remove(self.lock_)
        return True

    def start_listen(self):
        """Create queue & new thread and start listen.

        """
        self.queue_ = Queue()
        """Queue: Queue to communicate in case this node
            sends request with new publish.

        """
        self.listener = Thread(target=self.listener)
        """Thread: Thread to serve requests."""
        self.listener.start()

    def all_node_sent(self, cmp_nodes):
        """Check if all nodes sent their responses.

        Args:
            cmp_nodes (:obj:`list` of :obj:`str`): List of nodes
                who sent their messages already.

        Returns:
            True if all nodes already responded.

        """
        logger.debug(
            "Comparing " +
            str(sorted(set(self.nodes_))) + " " +
            str(sorted(set(cmp_nodes))) + " " +
            str(sorted(set(self.nodes_)) == sorted(set(cmp_nodes))))
        return sorted(set(self.nodes_)) == sorted(set(cmp_nodes))

    def sources_already_in_queue(self, cmp_nodes):
        """Check if all nodes sent their responses.

        Args:
            cmp_nodes (:obj:`list` of :obj:`str`): List of nodes
                who sent their messages already.

        Returns:
            True if all nodes already responded.

        """
        global request_queue_
        req_nodes = [k[0] for k in request_queue_]
        for i in req_nodes:
            if i not in cmp_nodes and i != self.whoami:
                cmp_nodes.append(i)
        logger.debug(
            "Comparing already in queue " +
            str(sorted(set(self.nodes_))) + " " +
            str(sorted(set(cmp_nodes))) + " " +
            str(sorted(set(self.nodes_)) == sorted(set(cmp_nodes))))
        return sorted(set(self.nodes_)) == sorted(set(cmp_nodes))

    def test_winner(self, request):
        """Wait for all the answers, sort them and return message
            with the biggest logical time.

        """
        global request_queue_, failed_nodes
        failed_nodes = []
        for node in self.nodes_:
            while 1:
                try:
                    self.comm_.send_request_nd(node, request)
                except socket.error:
                    failed_nodes.append(node)
                    break
                else:
                    try:
                        message = self.queue_.get(True, 1)
                    except queue.Empty:
                        self.comm_.send_request_nd(node, request)
                    else:
                        if message['message'] not in request_queue_:
                            request_queue_.append(message['message'])
                        break

        # pick message with the biggest timestamp
        request_queue_.sort(key=lambda x: x[1])
        head = request_queue_[0]
        tail = request_queue_[-1]
        logging.debug("request_queue_ " + str(request_queue_))
        # if it is our message, we got the lock!
        self.timer_.timer_ = tail[1] + 1  # setting max timer value
        # try to find if somebody else haven't got lock with same time
        times_ = list(
            filter(
                lambda x: x[1] == head[1],
                request_queue_
            )
        )
        logging.debug("times_ " + str(times_))
        times_.sort(key=lambda x: x[0])
        logging.debug("sorted_hosts_ " + str(times_))
        head = times_[0]
        if head == request:
            logging.info("Got lock")
            return True
        return False

    def share_var(self, message):
        global shared_var
        self.comm_.broadcast_var(message)
        shared_var = message

    def get_var(self):
        global shared_var
        return shared_var

    def listener(self):
        """Listen on all messages and forward them into queue if
            lock is requested or forward content of node queue.

        """
        global request_queue_, end_flag, shared_var
        while 1:
            message = self.comm_.receive_()
            logger.debug('Received message: ' + str(message))
            if message['type'] == 'end' and message['source'] == self.whoami:
                return
            elif message['type'] == 'response':
                self.queue_.put(message)
            elif message['type'] == 'request':
                request = message['message']
                if request not in request_queue_:
                    request_queue_.append(request)
                request_queue_.sort(key=lambda x: x[1])
                head = request_queue_[0]
                tail = request_queue_[-1]
                self.timer_.timer_ = tail[1] + 1
                logger.debug('request_queue_ ' + str(request_queue_))
                times_ = list(
                    filter(
                        lambda x: x[1] == head[1],
                        request_queue_
                    )
                )
                logging.debug("times_ " + str(times_))
                times_.sort(key=lambda x: x[0])
                logging.debug("sorted_hosts_ " + str(times_))
                head = times_[0]
                logger.debug('head value ' + str(head))
                (ip, port) = self.comm_.get_targets(message['source'])
                self.comm_.send_response(ip, port, head)
            elif message['type'] == 'release':
                logger.info('Releasing lock ' + str(message['message']))
                if message['message'] in request_queue_:
                    request_queue_.remove(message['message'])
                if end_flag and len(request_queue_) == 0:
                    (ip, port) = self.comm_.get_targets(self.whoami)
                    self.comm_.send_end(ip, port)
            elif message['type'] == 'var':
                logger.info('Received new var ' + str(message['message']))
                shared_var = str(message['message'])
            else:
                logger.info('This was not covered ' + str(message))
            if end_flag:
                return

    def finnish(self):
        """Send message to local node to end listenning and just end.

        """
        global end_flag, request_queue_
        end_flag = True
        for i in request_queue_:
            if i[0] == self.whoami:
                self.comm_.broadcast_release(i)
                request_queue_.remove(i)
        (ip, port) = self.comm_.get_targets(self.whoami)
        self.comm_.send_end(ip, port)
