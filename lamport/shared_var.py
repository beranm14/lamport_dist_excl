from .lamport import lamport


class shared_var:
    """Share variable across topology of nodes.

    This application uses lock to write something to the variable.
    But Lamport is much simplier. If the node reconnect, it does
    not have any chance to get variable in Lamport sense of way.

    Solution is to use input queue to keep the variable, that is much
    more simpler. That is done in `lamport_var.py`.

    """

    def register(self, whoami, path_to_nodes):
        """Register node into topology.

        Args:
            whoami (str): String with name of node.
            path_to_nodes (str): Path to yam with other
                nodes description.
        """
        self.lamp = lamport(whoami, path_to_nodes)

    def write_var(self, message):
        """Write shared variable into the topology.

        Args:
            message (str): String with message to the topology.
        """
        if self.lamp.lock():
            self.lamp.share_var(message)
            self.lamp.unlock()
            return True
        return False

    def read_var(self):
        """This works until the node restarts, message is not kept in
            queue, there is only place for locks, that's why in this case
            it is not right solution of the problem.

        Returns:
            Shared variable.
        """
        return self.lamp.get_var()

    def unregister(self):
        """End everything and send `end` to local socket.
        """
        self.lamp.finnish()
