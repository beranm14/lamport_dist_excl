from lamport.lamport_var import lamport_var
import readchar
from argparse import ArgumentParser


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
    shr_var = lamport_var(whoami=args.whoami, path_to_nodes=args.nodes)
    tmp = ""
    while 1:
        ch = readchar.readchar()
        tmp = shr_var.read_var()
        tmp = tmp + ch
        if str(ch) == '!':
            shr_var.finnish()
            return
        elif shr_var.publish(tmp):
            print(tmp)
        print(shr_var.read_var())


if __name__ == "__main__":
    main()
