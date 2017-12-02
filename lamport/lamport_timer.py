from random import randint


class lamport_timer:

    timer_ = randint(0, 1000)

    def timer_incr(self):
        self.timer_ = self.timer_ + 1
