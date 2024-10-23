from flask import request, Flask, render_template, jsonify, Response
from document_analyzer.analyzers.offerte import parse_offerte_file
from document_analyzer.analyzers.enrichLijnItems import parse_json
from document_analyzer.chat_models.azure import init_azure_chat
from document_analyzer.responses.json_response import build_json_response
from document_analyzer.persistence.file_storage import Document
from document_analyzer.tools.custom.model import init_custom_ocr_tool
from werkzeug.exceptions import HTTPException

api = Flask(__name__, template_folder='templates')


@api.route("/analyze_multi", methods=["POST"])
def analyze_multi():
    if request.files["file"].filename == '':
        raise HTTPException('none or too many docs', Response("no file uploaded", status=400))

    with Document(request.files["file"]) as document:
        ocr = init_custom_ocr_tool()
        model = init_azure_chat()

        result_dict = parse_offerte_file(document.filename, model, ocr)
        result_json = build_json_response(result_dict)
    return parse_json(result_json, model)


@api.route("/analyze", methods=["POST"])
def analyze():
    if request.files["file"].filename == '':
        raise HTTPException('none or too many docs', Response("no file uploaded", status=400))
    with Document(request.files["file"]) as document:
        ocr = init_custom_ocr_tool()
        model = init_azure_chat()

        result_dict = parse_offerte_file(document.filename, model, ocr)

    return build_json_response(result_dict)


@api.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@api.route("/hoofdstuk", methods=["GET"])
def hoofdstukken():
    return render_template("hoofdstukken.html")
