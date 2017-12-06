from .lamport import lamport
import logging
logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger(__name__)


class shared_var:

    def register(self, whoami, path_to_nodes):
        self.lamp = lamport(whoami, path_to_nodes)

    def write_var(self, message):
        if self.lamp.lock():
            self.lamp.share_var(message)
            self.lamp.unlock()
            return True
        return False

    def read_var(self):
        return self.lamp.get_var()

    def unregister(self):
        self.lamp.finnish()
