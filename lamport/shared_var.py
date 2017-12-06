from .lamport import lamport


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
        # this is bad in case of restart
        return self.lamp.get_var()

    def unregister(self):
        self.lamp.finnish()
