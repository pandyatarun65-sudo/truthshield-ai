"""Upload validation (type, size) + light image analysis (decode check, optional OCR)."""
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

from ..config import settings

ALLOWED = {
    "image": {".jpg", ".jpeg", ".png", ".webp", ".gif"},
    "video": {".mp4", ".webm", ".mov"},
    "audio": {".mp3", ".wav", ".ogg", ".m4a"},
}


def _kind_for(filename: str, content_type: str):
    ext = Path(filename).suffix.lower()
    for kind, exts in ALLOWED.items():
        if ext in exts and (content_type or "").startswith(kind):
            return kind, ext
    raise HTTPException(400, "Invalid file. Allowed: images (jpg, png, webp, gif), video (mp4, webm, mov), audio (mp3, wav, ogg, m4a).")


async def save_upload(file: UploadFile, directory: str | None = None, only: str | None = None):
    """Validate and store an upload. Returns (stored_filename, kind, ocr_text)."""
    kind, ext = _kind_for(file.filename or "", file.content_type or "")
    if only and kind != only:
        raise HTTPException(400, f"Only {only} files are allowed here.")
    limit = settings.MAX_UPLOAD_MB * 1024 * 1024
    data = bytearray()
    while chunk := await file.read(1024 * 1024):
        data.extend(chunk)
        if len(data) > limit:
            raise HTTPException(413, f"File too large. Maximum size is {settings.MAX_UPLOAD_MB} MB.")
    ocr_text = None
    if kind == "image":
        ocr_text = _check_image(bytes(data))
    folder = Path(directory or settings.UPLOAD_DIR)
    folder.mkdir(parents=True, exist_ok=True)
    name = f"{uuid.uuid4().hex}{ext}"
    (folder / name).write_bytes(bytes(data))
    return name, kind, ocr_text


def _check_image(data: bytes):
    """Verify the file really is an image (OpenCV) and try OCR if pytesseract is installed."""
    try:
        import cv2
        import numpy as np
    except ImportError:
        return None
    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(400, "Invalid file. The image could not be decoded.")
    try:
        import pytesseract
        text = pytesseract.image_to_string(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)).strip()
        return text[:2000] or None
    except Exception:  # tesseract binary not installed -> OCR skipped
        return None
