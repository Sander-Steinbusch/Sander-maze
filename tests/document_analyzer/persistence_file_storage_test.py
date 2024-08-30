import os.path
from pathlib import Path

from werkzeug.datastructures import FileStorage
from document_analyzer.persistence.file_storage import Document
from os.path import exists
from pytest import fixture

FILENAME = "invoice.pdf"
FILE_LOCATION = os.path.join("documents", FILENAME)


@fixture
def request_file():
    Path("documents").mkdir(parents=True, exist_ok=True)

    return FileStorage(filename=FILENAME)


class TestGivenTemporaryFileWhenInit:
    def test_then_file_not_created(self, request_file):
        _ = Document(request_file)

        assert not exists(FILE_LOCATION)


class TestGivenTemporaryFileWhenEnter:
    def test_then_file_is_created(self, request_file):
        with Document(request_file) as _:
            assert exists(FILE_LOCATION)

    def test_then_filename_has_expected_value(self, request_file):
        with Document(request_file) as temp_file:
            assert temp_file.filename == FILE_LOCATION


class TestGivenTemporaryFileWhenExit:
    def test_then_file_is_removed(self, request_file):
        with Document(request_file) as _:
            pass

        assert not exists(FILE_LOCATION)


class TestGivenTemporaryFileWhenExitWithException:
    def test_file_removed_on_exception(self, request_file):
        try:
            with Document(request_file) as _:
                raise Exception("error")
        except Exception:
            assert not exists(FILE_LOCATION)
