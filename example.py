from lamport.lamport import lamport
import time
from argparse import ArgumentParser
import random
import pause
import datetime


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

    print("==================================================================")
    print("==================  GETTING FIRST LOCK ===========================")
    print("MULTIPLE PROCESSES TRY TO GET THE LOCK WITH LITTLE TIME DIFFERENCE")
    print("==================================================================")
    now = datetime.datetime.now()
    now_minutes = now.replace(second=0, microsecond=0)
    now_plus_1 = now_minutes + datetime.timedelta(minutes=1.15)
    print("Setting same time till " + str(now_plus_1))
    pause.until(now_plus_1)

    time.sleep(random.randint(0, 10) / 10)
    lock = lamp.lock()
    if lock:
        print("Locked")
        time.sleep(10)
        lamp.unlock()
        print("Unlocked")
    else:
        print("Couldn't get a lock")

    print("==================================================================")
    """
    time.sleep(10)
    print("==================================================================")
    print("=================  GETTING SECOND LOCK ===========================")
    print("MULTIPLE PROCESSES TRY TO GET THE LOCK WITH AT THE SAME TIME")
    print("==================================================================")
    time.sleep(10)
    now = datetime.datetime.now()
    now_minutes = now.replace(second=0, microsecond=0)
    now_plus_1 = now_minutes + datetime.timedelta(minutes=1)
    print("Setting same time till " + str(now_plus_1))
    pause.until(now_plus_1)

    lock = lamp.lock()
    if lock:
        print("Locked")
        time.sleep(10)
        lamp.unlock()
        print("Unlocked")
    else:
        print("Couldn't get a lock")
    lamp.finnish()
    print("==================================================================")
    print("==================================================================")
    print("==================================================================")
    """


if __name__ == "__main__":
    main()
