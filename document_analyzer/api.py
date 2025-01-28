import asyncio
import io
import os
import threading
from flask import request, Flask, render_template, Response, jsonify, make_response
from document_analyzer.analyzers.document import parse_extraction_prompt, parse_enrich_abbreviation, parse_enrich_sum, \
    parse_enrich_chapter
from document_analyzer.chat_models.azure_chat import init_azure_chat
from document_analyzer.persistence.file_storage import Document
from document_analyzer.tools.custom.model import init_custom_ocr_tool
from werkzeug.exceptions import HTTPException
import uuid
import pyodbc


api = Flask(__name__, template_folder='templates')
VALID_API_KEY = os.getenv('API_KEY')
ODBC_KEY = os.getenv('ODBC_KEY')
print(VALID_API_KEY)
def api_key_required(f):
    def decorated(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        if not api_key or api_key != VALID_API_KEY:
            return jsonify({'message': 'Invalid or missing API key!'}), 403
        return f(*args, **kwargs)
    return decorated

def get_db_connection():
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "Server=tcp:sandermaze.database.windows.net,1433;"
        "Database=sandermaze;"
        "Uid=sandermaze_admin;"
        "Pwd=" + str(ODBC_KEY) + ";"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;")
    return conn

def run_background_task(file_content, file_name, unique_id):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # file content needs to be converted to object with name property for Document class (better way?)
    file = io.BytesIO(file_content)
    file.filename = file_name
    file.read = lambda: file_content
    loop.run_until_complete(process_document(file, unique_id))
    loop.close()

def create_db_record(unique_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "insert into DEX_DOCUMENTS (id, status) values (?, ?)",
        (unique_id, 'P')
    )
    conn.commit()
    cursor.close()
    conn.close()

async def store_result(unique_id, content):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE DEX_DOCUMENTS SET json_result = ?, status = ? WHERE id = ?",
        (content, 'D', unique_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

async def process_document(file, unique_id):
    async with Document(file) as document:
        ocr = await init_custom_ocr_tool()
        chat_model = await init_azure_chat()

        result_extraction = await parse_extraction_prompt(document.filename, chat_model, ocr)
        result_extraction_enrich_abbr = await parse_enrich_abbreviation(result_extraction.content, chat_model)
        result_extraction_enrich_sum = await parse_enrich_sum(result_extraction_enrich_abbr.content, chat_model)
        result_extraction_enrich_chapter = await parse_enrich_chapter(result_extraction_enrich_sum.content, chat_model)

        await store_result(unique_id, result_extraction_enrich_chapter.content)

@api.route("/analyze_doc_job", methods=["POST"], endpoint="analyze_doc_job")
@api_key_required
def analyze_doc_job():
    if request.files["file"].filename == '':
        raise HTTPException('no documents added', Response("no file uploaded", status=400))

    unique_id = str(uuid.uuid4())
    create_db_record(unique_id)

    # Read file content into memory, because cannot be done in async method
    file_content = request.files["file"].read()
    file_name = request.files["file"].filename
    threading.Thread(target=run_background_task, args=(file_content, file_name, unique_id)).start()

    return jsonify({'id': unique_id})

@api.route("/status/<string:id>", methods=["GET"], endpoint="status")
@api_key_required
def check_status(id):
    if not id:
        return jsonify({'message': 'Invalid or missing ID!'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, status FROM DEX_DOCUMENTS WHERE id = ?", (id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row:
        return jsonify({'id': row[0], 'status': row[1]}), 200
    else:
        return jsonify({'message': 'ID not found!'}), 404

@api.route("/download/<string:id>", methods=["GET"], endpoint="download")
@api_key_required
def download_result(id):
    if not id:
        return jsonify({'message': 'Invalid or missing ID!'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT json_result FROM DEX_DOCUMENTS WHERE id = ?", (id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row and row[0]:
        response = make_response(row[0])
        response.headers['Content-Type'] = 'application/json'
        return response, 200
    else:
        return jsonify({'message': 'ID not found or no result available!'}), 404

@api.route("/delete/<string:id>", methods=["DELETE"], endpoint="delete")
@api_key_required
def delete_record(id):
    if not id:
        return jsonify({'message': 'Invalid or missing ID!'}), 400

    force_delete = request.args.get('force', default=False, type=bool)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM DEX_DOCUMENTS WHERE id = ?", (id,))
    row = cursor.fetchone()

    if not row:
        cursor.close()
        conn.close()
        return jsonify({'message': 'ID not found!'}), 404

    status = row[0]
    if status != 'D' and not force_delete:
        cursor.close()
        conn.close()
        return jsonify({'message': 'Cannot delete record unless status is "D" or force delete is specified!'}), 403

    cursor.execute("DELETE FROM DEX_DOCUMENTS WHERE id = ?", (id,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'Record deleted successfully!'}), 204

@api.route("/", methods=["GET"], endpoint="index")
@api_key_required
def index():
    return render_template("index.html")