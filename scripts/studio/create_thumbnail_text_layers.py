from PIL import Image, ImageDraw, ImageFont
import textwrap

from utils.root import root
from utils.get_json import load_or_create_json
from utils.logger import log
from utils.constants import sep
from utils.phase_logger import phase

# === SETTINGS ===
width, height = 1376, 928
font_path = root / "assets" / "Montserrat-ExtraBold.ttf"
font_size = 45
text_color = (255, 255, 255, 255)
shadow_color = (0, 0, 0, 255)
shadow_offset = (4, 4)
text_y = 770
margin_x = 100
max_text_width = width - 2 * margin_x

output_dir = root / "resources" / "thumbnail_text_layers"
output_dir.mkdir(parents=True, exist_ok=True)

@phase("CREATE THUMBNAILS")
def create_thumbnails(force_rewrite: bool = False):
    log.magenta.bold.underline("Did you check/fix video labels for automatic thumbnail generation?")
    check_confirm = input("If you did type <Yes>, otherwise click any button to stop.")
    if check_confirm.lower() != "yes":
        raise KeyboardInterrupt()


    metas = load_or_create_json(root / "resources" / "videos_meta.json")

    # === FORCE REWRITE CLEANUP ===
    if force_rewrite:
        for old_file in output_dir.iterdir():
            if old_file.is_file():
                old_file.unlink()
        log.yellow("Folder cleared due to force_rewrite=True")

    # === LOAD FONT ===
    try:
        font = ImageFont.truetype(str(font_path), font_size)
    except IOError:
        log.red.bold("ERROR: Font not found!")
        return

    # === PROCESS EACH ENTRY ===
    for fp, meta in metas.items():
        output_file = output_dir / f"{meta['filename']}{sep}{fp}.png"

        if not force_rewrite:
            # Skip if file exists
            if output_file.exists():
                log.yellow(f"Skipping (already exists): {output_file.name}")
                continue

        # === DRAW IMAGE ===
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        wrapped = textwrap.wrap(meta["label"], width=40)
        lines = "\n".join(wrapped)

        # Text bounding box
        text_bbox = draw.multiline_textbbox((0, 0), lines, font=font)
        text_w = text_bbox[2] - text_bbox[0]
        text_x = (width - text_w) // 2

        # Shadow
        draw.multiline_text(
            (text_x + shadow_offset[0], text_y + shadow_offset[1]),
            lines,
            font=font,
            fill=shadow_color,
            align="center"
        )

        # Main text
        draw.multiline_text(
            (text_x, text_y),
            lines,
            font=font,
            fill=text_color,
            align="center"
        )

        # === SAVE ===
        img.save(output_file, "PNG")
        log.green(f"Saved: {output_file.name}")

    log.green.bold(f"Completed. Output folder: {output_dir}")


if __name__ == "__main__":
    create_thumbnails()
