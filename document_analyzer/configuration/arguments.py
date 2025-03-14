from argparse import ArgumentParser

def get_arguments():
    parser = ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-p", "--port", help="Specify the port to listen to. Default is 8000.",
                        default=8000, type=int)
    return parser.parse_args()
    