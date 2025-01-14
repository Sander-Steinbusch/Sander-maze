from document_analyzer.api import api
from waitress import serve
from document_analyzer.configuration import get_arguments

if __name__ == "__main__":
    args = get_arguments()

    if args.verbose:
        print("Application started")

    serve(api, host="0.0.0.0", port=args.port)