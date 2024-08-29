from json import loads
from flask import Flask, request
from document_analyzer.responses.json_response import build_json_response
from mock_document_analyzer.data import get_test_data

mock_api = Flask(__name__)

@mock_api.route("/analyze", methods=["POST"])
def analyze():
	return build_json_response(
		get_test_data()
	)

@mock_api.route("/analyze/segmented", methods=["POST"])
def analyze_segmented():
	return build_json_response(
		get_test_data()
	)

@mock_api.route("/translate", methods=["POST"])
def translate():
	dict_obj = loads(request.data)
	language = dict_obj["language"]
	
	for text in dict_obj["texts"]:
		text["text"] = "translated to " + language + ": " + text["text"]
		
	return dict_obj["texts"]