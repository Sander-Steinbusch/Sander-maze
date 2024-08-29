from argparse import ArgumentParser

def get_arguments():
    parser = ArgumentParser()
    parser.add_argument("-m", "--mock-data", help="return test data.", action="store_true")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-p", "--port", help="Specify the port to listen to. Default is 8080.", 
                        default=8080, type=int)
    return parser.parse_args()
    