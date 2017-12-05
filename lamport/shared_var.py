from lamport import lamport


class shared_var:

    shared_var = ""

    def register(self, whoami, path_to_nodes):
        self.lamp = lamport(whoami, path_to_nodes)

    def write_var(self, message):
        if self.lamp.lock():
            self.lamp.share_var(message)
            self.shared_var = message
            self.lamp.unlock()
            return True
        return False

    def read_var(self):
        self.shared_var = self.lamp.get_var()
        return self.shared_var

    def unregister(self):
        self.lamp.finnish()
