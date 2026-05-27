from hashlib import md5
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4

from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

from team_finder.constants import (
    AVATAR_CANVAS_SIZE,
    AVATAR_COLORS,
    AVATAR_FONT_SIZE_RATIO,
    AVATAR_TEXT_COLOR,
    AVATAR_TEXT_VERTICAL_OFFSET_RATIO,
    USER_PHONE_MAX_LENGTH,
)

PHONE_PREFIX = "+7"
FONT_PATH = (
    Path(settings.BASE_DIR)
    / "static"
    / "fonts"
    / "Neue_Haas_Grotesk_Display_Pro_75_Bold.otf"
)


def normalize_phone(phone):
    value = (phone or "").strip()
    if not value:
        return value
    if value.startswith("8") and len(value) == 11 and value.isdigit():
        return f"{PHONE_PREFIX}{value[1:]}"
    if (
        value.startswith("+7")
        and len(value) == USER_PHONE_MAX_LENGTH
        and value[1:].isdigit()
    ):
        return value
    raise ValueError("Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX.")


def is_github_url(url):
    if not url:
        return True
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return False
    hostname = (parsed.hostname or "").lower()
    return hostname == "github.com" or hostname.endswith(".github.com")


def get_avatar_font(image_size):
    font_size = round(image_size * AVATAR_FONT_SIZE_RATIO)
    try:
        return ImageFont.truetype(str(FONT_PATH), font_size)
    except OSError:
        return ImageFont.load_default(size=font_size)


def generate_avatar(name):
    text = (name or "?").strip()[:1].upper() or "?"
    color_index = int(md5(text.encode("utf-8")).hexdigest(), 16) % len(AVATAR_COLORS)
    image = Image.new(
        "RGB",
        (AVATAR_CANVAS_SIZE, AVATAR_CANVAS_SIZE),
        AVATAR_COLORS[color_index],
    )
    draw = ImageDraw.Draw(image)
    font = get_avatar_font(AVATAR_CANVAS_SIZE)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x_position = (AVATAR_CANVAS_SIZE - text_width) / 2
    y_position = (
        (AVATAR_CANVAS_SIZE - text_height) / 2
        - AVATAR_CANVAS_SIZE * AVATAR_TEXT_VERTICAL_OFFSET_RATIO
    )
    draw.text(
        (x_position, y_position),
        text,
        fill=AVATAR_TEXT_COLOR,
        font=font,
    )

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue(), name=f"avatar_{uuid4().hex}.png")
