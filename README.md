# AIDA – Document Extraction API

A Python back-end REST API that extracts structured pricing data (basis/header
information and line items) from uploaded invoices and offers (PDFs or images).

Documents are processed asynchronously: an upload starts a background job, and
the caller polls for status/progress and downloads the JSON result when it is
ready. Results are persisted in Azure SQL.

## How it works

Instead of first flattening the document to plain text with OCR, AIDA renders
each PDF page to an image and passes those images **directly to a vision-capable
Azure OpenAI model**. This preserves the full visual layout of the
invoice/offer (tables, columns, alignment), which carries a lot of the context
that is otherwise lost when the document is reduced to flat text.

Pipeline:

1. The uploaded file is stored temporarily on disk.
2. Each page is rendered to a PNG image with [PyMuPDF](https://pymupdf.readthedocs.io/)
   (image uploads are passed through as-is).
3. The images are sent to the model, which returns:
   - **Basis information** (author, document date, document number, document type)
     via structured output.
   - **Line items** (description, quantity, unit, price, reduction, delivery,
     chapter, …), page-chunked to stay within the model's context window and
     then merged.
4. For non–extract-only jobs, optional enrichment steps run (abbreviation
   expansion, summing of identical items, chapter classification).
5. The merged JSON result is stored in Azure SQL.

## Requirements

- Python 3.11+
- An [ODBC Driver 18 for SQL Server](https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server)
  (required by `pyodbc`).
- An Azure OpenAI resource with a **vision-capable** deployment.

## Setup

### Virtual environment

```bash
python -m venv .venv
# Activate it (see the venv docs for your OS/shell), then:
pip install -r requirements.txt
```

`requirements.txt` lists only the direct dependencies. To produce a fully pinned
lock file for a deployment, run `pip freeze > requirements.lock.txt`.

### Configuration

Azure OpenAI settings live in [`configuration.ini`](configuration.ini):

- `openai_api_base` – Azure OpenAI endpoint.
- `openai_api_version` – Azure OpenAI API version.
- `deployment_name` – name of the vision-capable deployment to use.

### Environment variables

| Variable         | Purpose                                                        |
| ---------------- | -------------------------------------------------------------- |
| `OPENAI_API_KEY` | Key for the Azure OpenAI resource.                             |
| `API_KEY`        | Value expected in the `x-api-key` request header.              |
| `ODBC_KEY`       | Password for the Azure SQL database connection.                |
| `SLOT_NAME`      | Set to `DEV` to also log INFO messages to the console.         |

> Note: Azure Document Intelligence / Cognitive Services is no longer used, so
> `AZURE_COGS_KEY` is no longer required.

## Running

```bash
python app.py -p 8000
```

Arguments:

- `-p`, `--port` – port to listen on (default `8000`).
- `-v`, `--verbose` – print a startup message.

The server is served with [waitress](https://docs.pylonsproject.org/projects/waitress/).

## API

All endpoints require an `x-api-key` header matching the `API_KEY` environment
variable.

| Method   | Path                          | Description                                              |
| -------- | ----------------------------- | ------------------------------------------------------- |
| `POST`   | `/analyze_doc_job`            | Upload a `file`; starts a job and returns its `id`. Add `?extract_only=true` to skip the enrichment steps. |
| `GET`    | `/status/<id>`                | Job status (`P`ending, running, `D`one, `F`ailed).      |
| `GET`    | `/progress/<id>`              | Progress percentage for a running job.                  |
| `GET`    | `/active_jobs`                | Currently running jobs.                                 |
| `GET`    | `/download/<id>`              | The JSON result and processing duration.                |
| `DELETE` | `/delete/<id>`                | Delete a record (only when done, or `?force=true`).     |
| `GET`    | `/`                           | Simple upload page.                                     |
| `GET`    | `/get_full_completion/<id>`   | Stored prompt + completion for a completion id (JSONL). |
| `GET`    | `/list_full_completions/`     | All stored prompts + completions (JSONL).               |
| `GET`    | `/list_completions`           | List of stored completion ids.                          |

Example:

```bash
curl -X POST "http://localhost:8000/analyze_doc_job?extract_only=true" \
  -H "x-api-key: $API_KEY" \
  -F "file=@invoice.pdf"
```

## Code style

Pre-commit hooks run [black](https://black.readthedocs.io/) and
[flake8](https://flake8.pycqa.org/). Install them with:

```bash
pre-commit install
```
