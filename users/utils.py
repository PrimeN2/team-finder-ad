from hashlib import md5
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4

from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont


PHONE_LENGTH = 12
PHONE_PREFIX = "+7"
FONT_PATH = (
    Path(settings.BASE_DIR)
    / "static"
    / "fonts"
    / "Neue_Haas_Grotesk_Display_Pro_75_Bold.otf"
)
AVATAR_COLORS = (
    "#F59E0B",
    "#EF4444",
    "#10B981",
    "#3B82F6",
    "#8B5CF6",
    "#14B8A6",
)


def normalize_phone(phone):
    value = (phone or "").strip()
    if not value:
        return value
    if value.startswith("8") and len(value) == 11 and value.isdigit():
        return f"{PHONE_PREFIX}{value[1:]}"
    if value.startswith("+7") and len(value) == PHONE_LENGTH and value[1:].isdigit():
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


def generate_avatar(name):
    text = (name or "?").strip()[:1].upper() or "?"
    color_index = int(md5(text.encode("utf-8")).hexdigest(), 16) % len(AVATAR_COLORS)
    image = Image.new("RGB", (256, 256), AVATAR_COLORS[color_index])
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype(str(FONT_PATH), 144)
    except OSError:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    x_position = (256 - (bbox[2] - bbox[0])) / 2
    y_position = (256 - (bbox[3] - bbox[1])) / 2 - 12
    draw.text((x_position, y_position), text, fill="#FFFFFF", font=font)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue(), name=f"avatar_{uuid4().hex}.png")
