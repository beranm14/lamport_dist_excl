from functools import reduce


class lamport_timer:

    timer_ = 0

    def __init__(self, whoami):
        self.timer_ = reduce((lambda x, y: x + y), bytes(whoami, 'UTF-8'))

    def timer_incr(self):
        self.timer_ = self.timer_ + 1
