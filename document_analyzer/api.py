from flask import request, Flask, render_template
from document_analyzer.analyzers.offerte import parse_offerte_file
from document_analyzer.chat_models.azure import init_azure_chat
from document_analyzer.responses.json_response import build_json_response
from document_analyzer.persistence.file_storage import Document
from document_analyzer.tools.custom.model import init_custom_ocr_tool

api = Flask(__name__,template_folder='templates')

@api.route("/doc", methods=["POST"])
def doc():
    with Document(request.files["file"]) as document:
        ocr = init_custom_ocr_tool()
        model = init_azure_chat()

        result_dict = parse_offerte_file(document.filename, model, ocr)

    return build_json_response(result_dict)

@api.route("/", methods=["GET"])
def index():
   return render_template("index.html")

@api.route("/hoofdstuk", methods=["GET"])
def hello():
   return render_template("hoofdstukken.html")