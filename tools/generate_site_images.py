from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


def _center_crop_to_ratio(img: Image.Image, ratio: float) -> Image.Image:
    w, h = img.size
    current = w / h
    if current > ratio:
        new_w = int(h * ratio)
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    new_h = int(w / ratio)
    top = (h - new_h) // 2
    return img.crop((0, top, w, top + new_h))


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _text_shadow(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, font, fill=(255, 255, 255)) -> None:
    draw.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0))
    draw.text((x, y), text, font=font, fill=fill)


def _generate_service_placeholder(
    *,
    hero: Image.Image,
    label: str,
    out_path: Path,
    logo_src: Path,
    size: tuple[int, int] = (800, 500),
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    img = _center_crop_to_ratio(hero, size[0] / size[1]).resize(size, Image.Resampling.LANCZOS)
    img = Image.blend(img, Image.new("RGB", img.size, (0, 0, 0)), 0.18)

    canvas = img.convert("RGBA")
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle((0, size[1] - 110, size[0], size[1]), fill=(10, 20, 30, 170))
    canvas = Image.alpha_composite(canvas, overlay)

    draw = ImageDraw.Draw(canvas)
    font_title = _load_font(40)
    font_sub = _load_font(24)

    title = label
    sub = "Midwest Flip LLC — Detroit & Metro Detroit"
    _text_shadow(draw, 28, size[1] - 98, title, font_title)
    _text_shadow(draw, 28, size[1] - 54, sub, font_sub, fill=(230, 235, 245))

    if logo_src.exists():
        logo = Image.open(logo_src).convert("RGBA")
        logo.thumbnail((96, 96))
        plate = Image.new("RGBA", (logo.size[0] + 18, logo.size[1] + 18), (255, 255, 255, 230))
        plate_draw = ImageDraw.Draw(plate)
        plate_draw.rounded_rectangle(
            (0, 0, plate.size[0] - 1, plate.size[1] - 1),
            radius=16,
            outline=(255, 255, 255, 255),
            width=2,
        )
        plate.alpha_composite(logo, (9, 9))
        canvas.paste(plate, (size[0] - plate.size[0] - 24, 24), plate)

    canvas.convert("RGB").save(out_path, quality=84, optimize=True, progressive=True)


def _generate_og_variant(*, hero: Image.Image, logo_src: Path, title: str, sub: str, out_jpg: Path) -> None:
    base = hero.resize((1200, 675), Image.Resampling.LANCZOS).crop((0, 22, 1200, 652))
    base = base.filter(ImageFilter.GaussianBlur(2))

    grad = Image.new("L", (1200, 630), 0)
    grad_draw = ImageDraw.Draw(grad)
    for x in range(1200):
        alpha = int(220 * (1 - (x / 1200) * 0.85))
        grad_draw.line([(x, 0), (x, 630)], fill=alpha)

    shade = Image.new("RGB", (1200, 630), (10, 20, 30))
    base = Image.composite(shade, base, grad)

    draw = ImageDraw.Draw(base)
    font_title = _load_font(76)
    font_sub = _load_font(34)
    font_small = _load_font(30)

    if logo_src.exists():
        logo = Image.open(logo_src).convert("RGBA")
        logo.thumbnail((180, 180))
        plate = Image.new("RGBA", (logo.size[0] + 34, logo.size[1] + 34), (255, 255, 255, 235))
        plate_draw = ImageDraw.Draw(plate)
        plate_draw.rounded_rectangle(
            (0, 0, plate.size[0] - 1, plate.size[1] - 1),
            radius=26,
            outline=(255, 255, 255, 255),
            width=2,
        )
        plate.alpha_composite(logo, (17, 17))
        base.paste(plate, (70, 70), plate)

    phone = "(313) 389-6324"
    _text_shadow(draw, 70, 290, title, font_title)
    _text_shadow(draw, 70, 385, sub, font_sub, fill=(230, 235, 245))

    pill_x, pill_y = 70, 470
    pill_w, pill_h = 360, 58
    pill = Image.new("RGBA", (pill_w, pill_h), (35, 131, 178, 240))
    pill_draw = ImageDraw.Draw(pill)
    pill_draw.rounded_rectangle(
        (0, 0, pill_w - 1, pill_h - 1),
        radius=18,
        outline=(255, 255, 255, 60),
        width=2,
    )
    base.paste(pill, (pill_x, pill_y), pill)
    _text_shadow(draw, pill_x + 18, pill_y + 12, phone, font_small)

    out_jpg.parent.mkdir(parents=True, exist_ok=True)
    base.save(out_jpg, quality=86, optimize=True, progressive=True)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    images_dir = root / "images"

    hero_src = images_dir / "40330379-1E1C-48C3-8971-1136EB901E58.jpg"
    logo_src = images_dir / "logo.png"

    out_og_jpg = images_dir / "og-image.jpg"
    out_og_webp = images_dir / "og-image.webp"
    out_og_service_areas_jpg = images_dir / "og-service-areas.jpg"
    out_hero_jpg = images_dir / "hero.jpg"
    out_hero_webp = images_dir / "hero.webp"

    if not hero_src.exists():
        raise FileNotFoundError(f"Missing hero source image: {hero_src}")

    # ---- HERO (1920x1080) ----
    hero = Image.open(hero_src).convert("RGB")
    hero = _center_crop_to_ratio(hero, 16 / 9)
    hero = hero.resize((1920, 1080), Image.Resampling.LANCZOS)

    # Darken slightly so text over hero stays readable
    hero = Image.blend(hero, Image.new("RGB", hero.size, (0, 0, 0)), 0.22)

    hero.save(out_hero_jpg, quality=82, optimize=True, progressive=True)
    hero.save(out_hero_webp, quality=78, method=6)

    # ---- OG (1200x630) ----
    _generate_og_variant(
        hero=hero,
        logo_src=logo_src,
        title="Midwest Flip LLC",
        sub="Home Remodeling Contractor — Detroit & Metro Detroit",
        out_jpg=out_og_jpg,
    )
    Image.open(out_og_jpg).save(out_og_webp, quality=82, method=6)

    # ---- OG variant used by service-areas.html (keep existing markup working) ----
    if not out_og_service_areas_jpg.exists():
        _generate_og_variant(
            hero=hero,
            logo_src=logo_src,
            title="Service Areas",
            sub="60+ Metro Detroit Cities — Midwest Flip LLC",
            out_jpg=out_og_service_areas_jpg,
        )

    # ---- Missing service placeholder JPGs (used by a few generated pages) ----
    service_images_dir = images_dir / "services"
    placeholders: list[tuple[str, Path]] = [
        ("Contact Us", service_images_dir / "contact-us.jpg"),
        ("Our Services", service_images_dir / "our-services.jpg"),
        ("Service Areas", service_images_dir / "service-areas.jpg"),
    ]
    for label, out_path in placeholders:
        if not out_path.exists():
            _generate_service_placeholder(hero=hero, label=label, out_path=out_path, logo_src=logo_src)

    print("Wrote:")
    print("-", out_hero_jpg.relative_to(root))
    print("-", out_hero_webp.relative_to(root))
    print("-", out_og_jpg.relative_to(root))
    print("-", out_og_webp.relative_to(root))
    if out_og_service_areas_jpg.exists():
        print("-", out_og_service_areas_jpg.relative_to(root))
    for _, out_path in placeholders:
        if out_path.exists():
            print("-", out_path.relative_to(root))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
