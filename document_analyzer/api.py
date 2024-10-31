from flask import request, Flask, render_template, Response
from document_analyzer.analyzers.offerte import parse_offerte_file
from document_analyzer.analyzers.document import parse_extraction_prompt, parse_enrich_abbr, parse_enrich_sum, \
    parse_enrich_chapter
from document_analyzer.chat_models.azure import init_azure_chat
from document_analyzer.responses.json_response import build_json_response
from document_analyzer.persistence.file_storage import Document
from document_analyzer.tools.custom.model import init_custom_ocr_tool
from werkzeug.exceptions import HTTPException

api = Flask(__name__, template_folder='templates')


@api.route("/analyze", methods=["POST"])
def analyze():
    if request.files["file"].filename == '':
        raise HTTPException('no documents added', Response("no file uploaded", status=400))
    with Document(request.files["file"]) as document:
        ocr = init_custom_ocr_tool()
        model = init_azure_chat()

        result_dict = parse_offerte_file(document.filename, model, ocr)

    return build_json_response(result_dict)


@api.route("/analyze_new", methods=["POST"])
def prompt():
    if request.files["file"].filename == '':
        raise HTTPException('no documents added', Response("no file uploaded", status=400))
    with Document(request.files["file"]) as document:
        ocr = init_custom_ocr_tool()
        chat_model = init_azure_chat()

        result_extraction = parse_extraction_prompt(document.filename, chat_model, ocr)
        result_extraction_enrich_abbr = parse_enrich_abbr(result_extraction.content, chat_model)
        result_extraction_enrich_sum = parse_enrich_sum(result_extraction_enrich_abbr.content, chat_model)
        result_extraction_enrich_chapter = parse_enrich_chapter(result_extraction_enrich_sum.content, chat_model)
    return result_extraction_enrich_chapter.content


@api.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@api.route("/hoofdstuk", methods=["GET"])
def hoofdstukken():
    return render_template("hoofdstukken.html")
