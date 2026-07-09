from werkzeug.utils import secure_filename
from os import makedirs, path, remove
import aiofiles
import asyncio

DOCUMENTS_DIR = "documents"


class Document(object):
    def __init__(self, request_file):
        self.request_file = request_file

    async def __aenter__(self):
        makedirs(DOCUMENTS_DIR, exist_ok=True)
        self.filename = path.join(DOCUMENTS_DIR, secure_filename(self.request_file.filename))
        async with aiofiles.open(self.filename, 'wb') as out_file:
            content = self.request_file.read()
            await out_file.write(content)
        return self

    async def __aexit__(self, *args):
        await asyncio.to_thread(remove, self.filename)
