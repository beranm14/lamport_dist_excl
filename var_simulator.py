from lamport.shared_var import shared_var
import readchar


def main():
    shr_var = shared_var()
    while 1:
        ch = readchar.readchar()
        tmp = shr_var.get_var()
        if shr_var.write_var(ch):
            shr_var
        if str(ch) == '!':
            return
        print(ch)

if __name__ == "__main__":
    main()
