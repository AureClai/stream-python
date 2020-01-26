# Script for modding stream :

# 1. Define functions for steps
# 2. Modify the process dict in the custom_process function to call the
# custom functions


def custom_process():
    # Importation of the original process
    from stream.main import get_stream_base_process
    Process = get_stream_base_process()
    #
    # Modify Below the functions of yout custom process
    # Exemple :
    # Process['import'] = my_import
    #
    # Here:

    #
    # End of function
    #
    return Process


#
#   CHANGING BELOW THIS IS UNRECOMMENDED !
#


def main(args):
    if len(args) == 0:
        sys.exit("Error : No file")
    else:
        filename = args[0]
        Process = custom_process()
        # Running stream
        from stream.main import run_simulation
        run_simulation(filename, custom_process=Process, saveS=True)


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
