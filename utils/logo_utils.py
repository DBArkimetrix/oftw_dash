import base64
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import cairosvg
import os
import re
import hashlib

# Path to logo folder — adjust if needed
logo_dir = Path("/home/dhb/dash_oftp/downloaded_logos")

# Cache to avoid re-encoding (in-memory for current session)
logo_cache = {}

# Optional: Path to a temporary cache directory for persistence
cache_dir = Path("/tmp/logo_cache")
cache_dir.mkdir(parents=True, exist_ok=True)


def get_logo_as_base64(logo_filename, height=30):
    """Encode the logo file as base64 string, using persistent cache if available"""
    if logo_filename in logo_cache:
        return logo_cache[logo_filename]

    file_path = logo_dir / logo_filename
    if not file_path.exists():
        return None

    # Hash to use for persistent cache filename
    cache_key = f"{logo_filename}_{height}"
    cache_hash = hashlib.md5(cache_key.encode()).hexdigest()
    cache_file = cache_dir / f"{cache_hash}.b64"

    if cache_file.exists():
        with open(cache_file, "r") as f:
            b64_image = f.read()
            logo_cache[logo_filename] = b64_image
            return b64_image

    try:
        if file_path.suffix.lower() == '.svg':
            png_data = cairosvg.svg2png(url=str(file_path), output_height=height)
            encoded = base64.b64encode(png_data).decode('ascii')
            b64_image = f"data:image/png;base64,{encoded}"
        else:
            with Image.open(file_path) as img:
                width = int(img.width * (height / img.height))
                img = img.resize((width, height), Image.LANCZOS)
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                encoded = base64.b64encode(buffer.getvalue()).decode('ascii')
                b64_image = f"data:image/png;base64,{encoded}"

        # Save to cache
        with open(cache_file, "w") as f:
            f.write(b64_image)

        logo_cache[logo_filename] = b64_image
        return b64_image

    except Exception as e:
        print(f"Error processing logo {logo_filename}: {e}")
        return None


def generate_fallback_initials_image(name: str, height: int = 30) -> str:
    """Generate a simple fallback image with initials if no logo is found"""
    initials = "".join([word[0].upper() for word in name.split() if word][:2])
    img = Image.new("RGB", (height, height), color=(220, 220, 220))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", size=int(height * 0.5))
    except:
        font = ImageFont.load_default()
    try:
        bbox = draw.textbbox((0, 0), initials, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except AttributeError:
        text_width, text_height = draw.textsize(initials, font=font)

    text_x = (height - text_width) // 2
    text_y = (height - text_height) // 2
    draw.text((text_x, text_y), initials, fill="black", font=font)

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def find_best_logo_match(donor_chapter, logo_mapping, use_fallback=True, height=30):
    """Find closest matching logo filename for a donor chapter, fallback to initials if needed"""
    if donor_chapter in logo_mapping:
        return logo_mapping[donor_chapter]

    donor_lower = donor_chapter.lower()
    for org_name, logo_file in logo_mapping.items():
        if org_name.lower() in donor_lower or donor_lower in org_name.lower():
            return logo_file

    donor_slug = re.sub(r'[^a-z0-9\s]', '', donor_lower).replace(' ', '-')
    for logo_file in os.listdir(logo_dir):
        file_stem = Path(logo_file).stem
        if donor_slug in file_stem or file_stem in donor_slug:
            return logo_file

    # Fallback to initials image
    if use_fallback:
        return generate_fallback_initials_image(donor_chapter, height=height)

    return None