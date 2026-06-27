import os
from typing import IO

from django.core.exceptions import ValidationError

from PIL import Image, UnidentifiedImageError


# Conservative limits to reduce risk.
MAX_UPLOAD_SIZE_BYTES = 2 * 1024 * 1024  # 2 MiB

ALLOWED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
}


# Pillow verification / parsing is authoritative.
# Extensions + content-type are only a first line of defense.
ALLOWED_MIME_PREFIXES = {
    "image/",
}


def _get_extension(filename: str) -> str:
    _, ext = os.path.splitext(filename or "")
    return ext.lower()


def validate_image_upload(uploaded_file, *, field_name: str = "image") -> None:
    """Validate a Django UploadedFile intended to be an image.

    Checks:
      - size limit
      - extension allowlist
      - MIME type sanity check (best-effort)
      - Pillow 'verify' + re-open to ensure decodability

    This prevents renamed executables and non-image payloads from being accepted.
    """

    if uploaded_file is None:
        return

    size = getattr(uploaded_file, "size", None)
    if size is None:
        # If size is unavailable, skip size enforcement.
        # Django usually provides it.
        pass
    else:
        if size > MAX_UPLOAD_SIZE_BYTES:
            raise ValidationError(
                {field_name: [f"File too large (max {MAX_UPLOAD_SIZE_BYTES // (1024*1024)} MiB)."]}
            )

    ext = _get_extension(getattr(uploaded_file, "name", ""))
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            {field_name: ["Unsupported file extension. Allowed: JPG, JPEG, PNG, GIF, WEBP."]}
        )

    # content_type is client-controlled; treat as hint only.
    content_type = getattr(uploaded_file, "content_type", "") or ""
    if content_type and not any(content_type.startswith(p) for p in ALLOWED_MIME_PREFIXES):
        raise ValidationError({field_name: ["Unsupported MIME type. Must be an image."]})

    # Pillow verification.
    # uploaded_file.file is typically a SpooledTemporaryFile.
    fileobj: IO[bytes] = getattr(uploaded_file, "file", None)
    if fileobj is None:
        raise ValidationError({field_name: ["Invalid upload stream."]})

    # Read/verify from the beginning.
    try:
        fileobj.seek(0)
        img = Image.open(fileobj)
        # verify() is strict and catches truncated/corrupted images.
        img.verify()

        # Re-open to ensure it's decodable after verify().
        fileobj.seek(0)
        Image.open(fileobj).load()
    except UnidentifiedImageError:
        raise ValidationError({field_name: ["Uploaded file is not a valid image."]})
    except Exception:
        raise ValidationError({field_name: ["Uploaded file could not be processed as an image."]})

