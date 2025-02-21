import asyncio
import io
import json
import os
import threading
import uuid
import pyodbc
import logging

from flask import request, Flask, render_template, Response, jsonify, make_response
from document_analyzer.analyzers.document import parse_extraction_prompt, parse_enrich_abbreviation, parse_enrich_sum, \
    parse_enrich_chapter
from document_analyzer.chat_models.azure_chat import init_azure_chat
from document_analyzer.persistence.file_storage import Document
from document_analyzer.tools.DbLoggingHandler import DbLoggingHandler
from document_analyzer.tools.custom.model import init_custom_ocr_tool
from werkzeug.exceptions import HTTPException
from datetime import datetime, timezone, timedelta

api = Flask(__name__, template_folder='templates')

VALID_API_KEY = os.getenv('API_KEY')
ODBC_KEY = os.getenv('ODBC_KEY')
belgian_offset = timedelta(hours=1)
running_jobs = {}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

conn_str = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "Server=tcp:sandermaze.database.windows.net,1433;"
    "Database=sandermaze;"
    "Uid=sandermaze_admin;"
    "Pwd=" + str(ODBC_KEY) + ";"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)
db_handler = DbLoggingHandler(conn_str)
formatter = logging.Formatter('%(message)s')
db_handler.setFormatter(formatter)
logger.addHandler(db_handler)

# Check the SLOT_NAME environment variable
slot_name = os.getenv('SLOT_NAME')
if slot_name == 'staging':
    # Enable console logging for the staging slot
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

print('Running')

def api_key_required(f):
    def decorated(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        if not api_key or api_key != VALID_API_KEY:
            return jsonify({'message': 'Invalid or missing API key!'}), 403
        return f(*args, **kwargs)

    return decorated

@api.errorhandler(HTTPException)
def handle_http_exception(e):
    response = make_response(jsonify({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    }), e.code)
    response.headers["Content-Length"] = len(response.get_data(as_text=True))
    response.content_type = "application/json"
    return response


def get_db_connection():
    try:
        conn = pyodbc.connect(conn_str)
        return conn
    except pyodbc.Error as e:
        logger.error(f"Database connection error: {e}")
        raise


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
    except Exception as e:
        logger.error(f"An error occurred during background task: {e}")
        running_jobs[unique_id]['status'] = 'failed'
    finally:
        running_jobs.pop(unique_id, None)
        loop.close()


def create_db_record(unique_id, start_timestamp):
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO DEX_DOCUMENTS (id, status, start_timestamp) VALUES (?, ?, ?)",
                (unique_id, 'P', start_timestamp)
            )
            conn.commit()
    except pyodbc.Error as e:
        logger.error(f"Error creating DB record: {e}")
    finally:
        if conn:
            conn.close()


async def store_result(unique_id, content, stop_timestamp):
    conn = None
    try:
        logger.info("Start store_result")
        stop_timestamp_str = stop_timestamp.strftime('%Y-%m-%d %H:%M:%S')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE DEX_DOCUMENTS SET json_result = ?, status = ?, stop_timestamp = CONVERT(DATETIME2, ?, 120) WHERE id = ?",
            (content, 'D', stop_timestamp_str, unique_id)
        )
        conn.commit()
        cursor.close()
    except pyodbc.Error as e:
        logger.error(f"Error storing result: {e}")
    finally:
        if conn:
            conn.close()


async def process_document(file, unique_id):
    try:
        async with Document(file) as document:
            ocr = await init_custom_ocr_tool()
            chat_model = await init_azure_chat()

            running_jobs[unique_id]['progress'] = 0

            result_extraction = await parse_extraction_prompt(document.filename, chat_model, ocr)
            logger.info("Finished result_extraction")
            running_jobs[unique_id]['progress'] = 25
            #result_extraction_enrich_abbr = await parse_enrich_abbreviation(result_extraction, chat_model)
            #logger.info("Finished result_extraction_enrich_abbr")
            #running_jobs[unique_id]['progress'] = 50
            #result_extraction_enrich_sum = await parse_enrich_sum(result_extraction_enrich_abbr.content, chat_model)
            #logger.info("Finished result_extraction_enrich_sum")
            #running_jobs[unique_id]['progress'] = 75
            #result_extraction_enrich_chapter = await parse_enrich_chapter(result_extraction_enrich_abbr.content, chat_model)
            logger.info("Finished result_extraction_enrich_chapter")
            running_jobs[unique_id]['progress'] = 100

            stop_timestamp = datetime.now(timezone.utc).astimezone(timezone(belgian_offset))

            #await store_result(unique_id, result_extraction_enrich_chapter.content, stop_timestamp)
            await store_result(unique_id, result_extraction, stop_timestamp)
            logger.info("Finished store_result")
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        running_jobs[unique_id]['status'] = 'failed'
    finally:
        await ocr.close()


async def process_document_lite(file, unique_id):
    try:
        async with Document(file) as document:
            running_jobs[unique_id]['progress'] = 0

            ocr = await init_custom_ocr_tool()
            chat_model = await init_azure_chat()
            logger.info("Finished ocr")
            running_jobs[unique_id]['progress'] = 25

            result_extraction = await parse_extraction_prompt(document.filename, chat_model, ocr)
            logger.info("Finished result_extraction")
            running_jobs[unique_id]['progress'] = 100

            stop_timestamp = datetime.now(timezone.utc).astimezone(timezone(belgian_offset))

            await store_result(unique_id, result_extraction, stop_timestamp)
            logger.info("Finished store_result")
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        running_jobs[unique_id]['status'] = 'failed'
    finally:
        await ocr.close()
@api.route("/analyze_doc_job", methods=["POST"], endpoint="analyze_doc_job")
@api_key_required
def analyze_doc_job():
    try:
        if request.files["file"].filename == '':
            raise HTTPException('No documents added', Response("No file uploaded", status=400))
        unique_id = str(uuid.uuid4())
        start_timestamp = datetime.now(timezone.utc).astimezone(timezone(belgian_offset))
        create_db_record(unique_id, start_timestamp)

        file_content = request.files["file"].read()
        file_name = request.files["file"].filename
        threading.Thread(target=run_background_task, args=(file_content, file_name, unique_id)).start()

        return jsonify({'id': unique_id})
    except HTTPException as e:
        return jsonify({'message': str(e)}), e.code
    except Exception as e:
        logger.error(f"Error in analyze_doc_job: {e}")
        return jsonify({'message': 'Internal server error'}), 500


@api.route("/status/<string:id>", methods=["GET"], endpoint="status")
@api_key_required
def check_status(id):
    try:
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
    except HTTPException as e:
        return jsonify({'message': str(e)}), e.code
    except Exception as e:
        logger.error(f"Error in check_status: {e}")
        return jsonify({'message': 'Internal server error'}), 500


@api.route("/download/<string:id>", methods=["GET"], endpoint="download")
@api_key_required
def download_result(id):
    try:
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
    except HTTPException as e:
        return jsonify({'message': str(e)}), e.code
    except Exception as e:
        logger.error(f"Error in check_status: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@api.route("/delete/<string:id>", methods=["DELETE"], endpoint="delete")
@api_key_required
def delete_record(id):
    try:
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
    except HTTPException as e:
        return jsonify({'message': str(e)}), e.code
    except Exception as e:
        logger.error(f"Error in check_status: {e}")
        return jsonify({'message': 'Internal server error'}), 500


@api.route("/progress/<string:id>", methods=["GET"], endpoint="progress")
@api_key_required
def check_progress(id):
    try:
        if not id:
            return jsonify({'message': 'Invalid or missing ID!'}), 400

        if id in running_jobs:
            return jsonify({'id': id, 'progress': running_jobs[id]['progress']})
        else:
            return jsonify({'message': 'ID not found or job not running!'}), 404
    except HTTPException as e:
        return jsonify({'message': str(e)}), e.code
    except Exception as e:
        logger.error(f"Error in check_status: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@api.route("/active_jobs", methods=["GET"], endpoint="active_jobs")
@api_key_required
def list_active_jobs():
    try:
        active_jobs = {job_id: details for job_id, details in running_jobs.items() if details['status'] == 'running'}
        return jsonify(active_jobs)
    except HTTPException as e:
        return jsonify({'message': str(e)}), e.code
    except Exception as e:
        logger.error(f"Error in check_status: {e}")
        return jsonify({'message': 'Internal server error'}), 500


@api.route("/", methods=["GET"], endpoint="index")
@api_key_required
def index():
    try:
        return render_template("index.html")
    except HTTPException as e:
        return jsonify({'message': str(e)}), e.code
    except Exception as e:
        logger.error(f"Error in check_status: {e}")
        return jsonify({'message': 'Internal server error'}), 500
