from werkzeug.utils import secure_filename
from os import path, remove
import aiofiles
import asyncio

class Document(object):
    def __init__(self, request_file):
        self.request_file = request_file

    async def __aenter__(self):
        self.filename = path.join("documents", secure_filename(self.request_file.filename))
        async with aiofiles.open(self.filename, 'wb') as out_file:
            content = self.request_file.read()
            await out_file.write(content)
        return self

    async def __aexit__(self, *args):
        await asyncio.to_thread(remove, self.filename)
