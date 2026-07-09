import base64
import logging
import mimetypes
import os

import pymupdf

logger = logging.getLogger(__name__)

# 150 DPI keeps text legible for the model while keeping the payload small.
DEFAULT_DPI = 150

# File types we pass through to the model as-is instead of rendering.
IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
    ".bmp",
    ".tif",
    ".tiff",
}


def render_document_to_images(path: str, dpi: int = DEFAULT_DPI) -> list[str]:
    """Render a document into a list of base64-encoded image data URIs, one per page.

    PDFs are rasterised page by page so the model can reason over the full visual
    layout of the invoice/offer (tables, columns, alignment) instead of a flattened
    text stream. Image uploads are passed through untouched.
    """
    extension = os.path.splitext(path)[1].lower()

    if extension in IMAGE_EXTENSIONS:
        return [_encode_image_file(path)]

    return _render_pdf(path, dpi)


def _render_pdf(path: str, dpi: int) -> list[str]:
    images: list[str] = []
    with pymupdf.open(path) as document:
        for page in document:
            pixmap = page.get_pixmap(dpi=dpi)
            png_bytes = pixmap.tobytes("png")
            images.append(_to_data_uri(png_bytes, "image/png"))

    logger.info("Rendered %d page(s) from %s", len(images), path)
    return images


def _encode_image_file(path: str) -> str:
    mime, _ = mimetypes.guess_type(path)
    with open(path, "rb") as handle:
        return _to_data_uri(handle.read(), mime or "image/png")


def _to_data_uri(data: bytes, mime: str) -> str:
    encoded = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{encoded}"
