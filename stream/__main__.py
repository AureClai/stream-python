from .main import runSimulation
import os

def main(args):
    if len(args)==0:
        sys.exit("You must specify scenario files in NPY format...")
        input()
    else:
        for arg in args:
            if arg.split('.')[-1]=='npy':
                exists = os.path.isfile(arg)
                if exists:
                    runSimulation(arg)
                else:
                    print(arg + " does not exists.")
                    input()
                    continue
            else:
                print(arg + "do not have the correct extension.")
                input()
                continue

# If stream is called from command line
if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
