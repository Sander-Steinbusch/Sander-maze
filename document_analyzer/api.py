import asyncio
import io
import json
import os
import threading
import uuid
import pyodbc

from flask import request, Flask, render_template, Response, jsonify, make_response
from document_analyzer.analyzers.document import parse_extraction_prompt, parse_enrich_abbreviation, parse_enrich_sum, \
    parse_enrich_chapter
from document_analyzer.chat_models.azure_chat import init_azure_chat
from document_analyzer.persistence.file_storage import Document
from document_analyzer.tools.custom.model import init_custom_ocr_tool
from werkzeug.exceptions import HTTPException
from datetime import datetime, timezone, timedelta

api = Flask(__name__, template_folder='templates')
VALID_API_KEY = os.getenv('API_KEY')
ODBC_KEY = os.getenv('ODBC_KEY')
belgian_offset = timedelta(hours=1)
running_jobs = {}

print('Running')

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
    running_jobs[unique_id] = {'status': 'running', 'start_timestamp': datetime.now(), 'progress': 0}
    try:
        loop.run_until_complete(process_document(file, unique_id))
    finally:
        running_jobs.pop(unique_id, None)
    loop.close()


def create_db_record(unique_id, start_timestamp):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "insert into DEX_DOCUMENTS (id, status, start_timestamp) values (?, ?, ?)",
        (unique_id, 'P', start_timestamp)
    )
    conn.commit()
    cursor.close()
    conn.close()


async def store_result(unique_id, content, stop_timestamp):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE DEX_DOCUMENTS SET json_result = ?, status = ?, stop_timestamp = ? WHERE id = ?",
        (content, 'D', stop_timestamp, unique_id)
    )
    conn.commit()
    cursor.close()
    conn.close()


async def process_document(file, unique_id):
    async with Document(file) as document:
        ocr = await init_custom_ocr_tool()
        chat_model = await init_azure_chat()

        # Initialize progress
        running_jobs[unique_id]['progress'] = 0

        result_extraction = await parse_extraction_prompt(document.filename, chat_model, ocr)
        running_jobs[unique_id]['progress'] = 25  # Update progress
        result_extraction_enrich_abbr = await parse_enrich_abbreviation(result_extraction.content, chat_model)
        running_jobs[unique_id]['progress'] = 50  # Update progress
        result_extraction_enrich_sum = await parse_enrich_sum(result_extraction_enrich_abbr.content, chat_model)
        running_jobs[unique_id]['progress'] = 75  # Update progress
        result_extraction_enrich_chapter = await parse_enrich_chapter(result_extraction_enrich_sum.content, chat_model)
        running_jobs[unique_id]['progress'] = 100  # Update progress

        stop_timestamp = datetime.now(timezone.utc).astimezone(timezone(belgian_offset)).strftime('%Y-%m-%d %H:%M:%S')

        await store_result(unique_id, result_extraction_enrich_chapter.content, stop_timestamp)
        await ocr.close()


@api.route("/analyze_doc_job", methods=["POST"], endpoint="analyze_doc_job")
@api_key_required
def analyze_doc_job():
    if request.files["file"].filename == '':
        raise HTTPException('no documents added', Response("no file uploaded", status=400))

    unique_id = str(uuid.uuid4())
    start_timestamp = datetime.now(timezone.utc).astimezone(timezone(belgian_offset)).strftime('%Y-%m-%d %H:%M:%S')

    create_db_record(unique_id, start_timestamp)

    # Read file content into memory, because cannot be done in async method
    file_content = request.files["file"].read()
    file_name = unique_id + "_" + request.files["file"].filename
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
    cursor.execute("SELECT json_result, start_timestamp, stop_timestamp FROM DEX_DOCUMENTS WHERE id = ?", (id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row and row[0]:
        json_result = row[0]
        start_timestamp = row[1]
        stop_timestamp = row[2]

        # Calculate duration
        if start_timestamp and stop_timestamp:
            duration = stop_timestamp - start_timestamp
            duration_seconds = duration.total_seconds()
        else:
            duration_seconds = None

        response_data = {
            'json_result': json.loads(json_result),
            'duration_seconds': duration_seconds
        }

        response = jsonify(response_data)
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


@api.route("/progress/<string:id>", methods=["GET"], endpoint="progress")
@api_key_required
def check_progress(id):
    if not id:
        return jsonify({'message': 'Invalid or missing ID!'}), 400

    if id in running_jobs:
        return jsonify({'id': id, 'progress': running_jobs[id]['progress']})
    else:
        return jsonify({'message': 'ID not found or job not running!'}), 404


@api.route("/active_jobs", methods=["GET"], endpoint="active_jobs")
@api_key_required
def list_active_jobs():
    active_jobs = {job_id: details for job_id, details in running_jobs.items() if details['status'] == 'running'}
    return jsonify(active_jobs)


@api.route("/", methods=["GET"], endpoint="index")
@api_key_required
def index():
    return render_template("index.html")
