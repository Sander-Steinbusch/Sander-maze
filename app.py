from document_analyzer.api import api
from mock_document_analyzer.api import mock_api
from waitress import serve
from document_analyzer.configuration import get_arguments

if __name__ == "__main__":
    args = get_arguments()

    if args.verbose:
        print("Application started")

    if args.mock_data:
        serve(mock_api, host="0.0.0.0", port=args.port)
    else:
        serve(api, host="0.0.0.0", port=args.port)