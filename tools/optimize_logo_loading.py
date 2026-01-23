from __future__ import annotations

import re
from pathlib import Path


SITE_ROOT = Path(__file__).resolve().parents[1]


LOGO_PRELOAD_RE = re.compile(
    r"<link\s+rel=\"preload\"[^>]*\bas=\"image\"[^>]*\bhref=\"[^\"]*logo\.svg\"",
    re.IGNORECASE,
)

HERO_PRELOAD_RE = re.compile(
    r"(<link\s+rel=\"preload\"[^>]*\bas=\"image\"[^>]*\bhref=\"[^\"]*hero\.webp\"[^>]*>\s*)",
    re.IGNORECASE,
)

ICON_LINK_RE = re.compile(r"<link\s+rel=\"icon\"", re.IGNORECASE)

# Targets only the header logo image.
LOGO_IMG_RE = re.compile(
    r"(<img\b(?=[^>]*\bclass=\"[^\"]*\blogo_img\b[^\"]*\")[^>]*\bsrc=\")([^\"]*logo\.svg)(\"[^>]*>)",
    re.IGNORECASE,
)


def _detect_newline(text: str) -> str:
    return "\r\n" if "\r\n" in text else "\n"


def _ensure_attr(img_tag: str, attr_name: str, attr_value: str) -> str:
    # If the attribute exists, leave as-is.
    if re.search(rf"\b{re.escape(attr_name)}=\"", img_tag, re.IGNORECASE):
        return img_tag

    # Insert before the final '>' (or '/>').
    m = re.search(r"\s*/?>\s*$", img_tag)
    if not m:
        return img_tag

    insert_at = m.start()
    return img_tag[:insert_at] + f' {attr_name}="{attr_value}"' + img_tag[insert_at:]


def optimize_file(path: Path) -> tuple[bool, list[str]]:
    original = path.read_text(encoding="utf-8")
    text = original
    nl = _detect_newline(text)
    changes: list[str] = []

    # 1) Add logo preload if missing (only if we can infer a logo.svg path).
    if not LOGO_PRELOAD_RE.search(text):
        logo_src_match = LOGO_IMG_RE.search(text)
        logo_href = None
        if logo_src_match:
            logo_href = logo_src_match.group(2)
        else:
            # As a fallback, detect plain occurrences of logo.svg in common paths.
            if "src=\"images/logo.svg\"" in text:
                logo_href = "images/logo.svg"
            elif "src=\"../images/logo.svg\"" in text:
                logo_href = "../images/logo.svg"

        if logo_href:
            preload_tag = (
                f'<link rel="preload" as="image" href="{logo_href}" '
                f'type="image/svg+xml">'
            )

            hero_m = HERO_PRELOAD_RE.search(text)
            if hero_m:
                insert_pos = hero_m.end(1)
                text = text[:insert_pos] + preload_tag + nl + nl + text[insert_pos:]
                changes.append("inserted logo preload after hero preload")
            else:
                icon_m = ICON_LINK_RE.search(text)
                if icon_m:
                    insert_pos = icon_m.start()
                    text = text[:insert_pos] + preload_tag + nl + nl + text[insert_pos:]
                    changes.append("inserted logo preload before icon link")
                else:
                    # Last resort: append near end of <head>.
                    head_close = text.lower().find("</head>")
                    if head_close != -1:
                        text = text[:head_close] + preload_tag + nl + text[head_close:]
                        changes.append("inserted logo preload before </head>")

    # 2) Ensure header logo uses high-priority fetch and async decoding.
    def repl(m: re.Match[str]) -> str:
        prefix, src, suffix = m.group(1), m.group(2), m.group(3)
        tag = prefix + src + suffix
        updated = _ensure_attr(tag, "fetchpriority", "high")
        updated = _ensure_attr(updated, "decoding", "async")
        return updated

    updated_text = LOGO_IMG_RE.sub(repl, text, count=1)
    if updated_text != text:
        text = updated_text
        changes.append("added fetchpriority/decoding to header logo")

    if text != original:
        path.write_text(text, encoding="utf-8")
        return True, changes

    return False, changes


def main() -> None:
    html_files = sorted(SITE_ROOT.rglob("*.html"))

    changed = 0
    touched: list[tuple[str, list[str]]] = []

    for path in html_files:
        # Skip obvious non-site artifacts if any.
        rel = path.relative_to(SITE_ROOT)
        # (keep receipt_design.html, etc. still fine)

        did_change, changes = optimize_file(path)
        if did_change:
            changed += 1
            touched.append((str(rel).replace("\\", "/"), changes))

    print(f"Processed {len(html_files)} HTML files")
    print(f"Updated {changed} files")
    if touched:
        print("\nFiles changed:")
        for rel, changes in touched:
            print(f"- {rel}: {', '.join(changes)}")


if __name__ == "__main__":
    main()
