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
failed_nodes = []
end_flag = False
shared_var = ""


class lamport:

    nodes_ = []
    lock_ = []

    def __init__(self, whoami, path_to_nodes='./lamport/nodes.yml'):
        print(path_to_nodes)
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
        global request_queue_, failed_nodes
        logger.info("Local lock requested")
        logger.debug("Local timer: %d", self.timer_.timer_)
        request = [self.whoami, self.timer_.timer_]
        # request_queue_.append(request)
        logger.debug("Request " + str(request))
        failed_nodes = self.comm_.broadcast_request(request)
        if self.test_winner(request):
            self.lock_ = request
            self.timer_.timer_incr()
            logger.debug("Lock taken")
            return True
        logger.debug("Lock already taken")
        self.comm_.broadcast_release(request)
        # request_queue_.remove(request)
        logger.debug("Requested for lock removal")
        self.lock_ = []
        return False

    def unlock(self):
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

    def test_winner(self, request):
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
        tail = request_queue_[-1]
        # if it is our message, we got the lock!
        self.timer_.timer_ = tail[1]  # setting max timer value
        # try to find if somebody else haven't got lock with same time
        times_ = list(
            filter(
                lambda x: x[1] == request[1],
                request_queue_
            )
        )
        logging.debug("times_ " + str(times_))
        if len(times_) > 1:
            logging.info("Somebody else got the same time")
            times_.sort(key=lambda x: x[0])
            logging.debug("sorted_hosts_ " + str(times_))
            tail = times_[-1]
            if tail == request:
                logging.info("Got lock")
                return True
            return False
        logging.debug(str(tail) + " == " + str(request))
        if tail == request:
            logging.info("Got lock")
            return True
        logging.info("Din't got lock")
        return False

    def share_var(self, message):
        global shared_var
        self.comm_.broadcast_var(message)

    def get_var(self):
        global shared_var
        return shared_var

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
                if message['message'][1] in [k[1] for k in request_queue_]:
                    already_in_message = list(
                        filter(
                            lambda x: x[1] == message['message'][1],
                            request_queue_
                        )
                    )[0]
                    logger.debug('tail value ' + str(already_in_message))
                    self.timer_.timer_ = already_in_message[1]
                    (ip, port) = self.comm_.get_targets(message['source'])
                    self.comm_.send_response(ip, port, already_in_message)
                else:
                    request_queue_.append(message['message'])
                    request_queue_.sort(key=lambda x: x[1])
                    tail = request_queue_[-1]
                    logger.debug('tail value ' + str(tail))
                    self.timer_.timer_ = tail[1]
                    (ip, port) = self.comm_.get_targets(message['source'])
                    self.comm_.send_response(ip, port, tail)
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
        global end_flag, request_queue_
        end_flag = True
        if len(request_queue_) == 0:
            (ip, port) = self.comm_.get_targets(self.whoami)
            self.comm_.send_end(ip, port)
