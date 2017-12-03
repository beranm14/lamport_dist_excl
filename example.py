from lamport.lamport import lamport
import time
from argparse import ArgumentParser
import random


def main():

    parser = ArgumentParser(
        description='Test application for Lamport shared variable in distributed system')
    parser.add_argument(
        '-w',
        action="store",
        dest="whoami",
        default='127.0.0.1:8991',
        help='Which machine is this.')
    parser.add_argument(
        '-n',
        action="store",
        dest="nodes",
        default='./lamport/nodes.yml',
        help='List of all nodes')

    args = parser.parse_args()

    lamp = lamport(whoami=args.whoami, path_to_nodes=args.nodes)

    time.sleep(10)
    lock = lamp.lock()
    if lock:
        print("Locked")
        time.sleep(10)
        lamp.unlock()
        print("Unlocked")
    else:
        print("Couldn't get a lock")

    lamp.finnish()


if __name__ == "__main__":
    main()
