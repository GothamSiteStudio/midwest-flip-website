from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse


IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".avif")


def _extract_image_like_refs(html: str) -> set[str]:
    refs: set[str] = set()

    # src/href attributes
    for m in re.finditer(r"\b(?:src|href)\s*=\s*\"([^\"]+)\"", html, flags=re.IGNORECASE):
        refs.add(m.group(1).strip())

    # meta og:image content
    for m in re.finditer(r"property\s*=\s*\"og:image\"\s+content\s*=\s*\"([^\"]+)\"", html, flags=re.IGNORECASE):
        refs.add(m.group(1).strip())

    # CSS url(...) in inline styles
    for m in re.finditer(r"url\(([^)]+)\)", html, flags=re.IGNORECASE):
        refs.add(m.group(1).strip().strip("\"'").strip())

    return refs


def _to_local_path(ref: str, html_file: Path, root: Path) -> Path | None:
    if not ref or ref.startswith("#") or ref.startswith("mailto:") or ref.startswith("tel:"):
        return None

    # absolute URL
    if ref.startswith("http://") or ref.startswith("https://"):
        parsed = urlparse(ref)
        if not parsed.path:
            return None
        path = parsed.path
        if path.startswith("/"):
            path = path[1:]
        return root / path

    # root-relative
    if ref.startswith("/"):
        return root / ref.lstrip("/")

    # relative to HTML file
    return (html_file.parent / ref).resolve()


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    html_files = list(root.rglob("*.html"))

    missing: list[tuple[str, str]] = []
    suspicious: list[tuple[str, str]] = []

    for html_file in html_files:
        text = html_file.read_text(encoding="utf-8", errors="ignore")
        refs = _extract_image_like_refs(text)

        for ref in refs:
            # keep only likely image references
            lower = ref.lower().split("?")[0].split("#")[0]
            if not (lower.endswith(IMAGE_EXTS) or "images/" in lower or "image" in lower):
                continue

            local = _to_local_path(ref, html_file, root)
            if local is None:
                continue

            # only care about assets inside project root
            try:
                local.relative_to(root)
            except Exception:
                continue

            if not local.exists():
                missing.append((str(html_file.relative_to(root)), ref))

            # flag HEIC/MOV if referenced (usually not web-safe)
            if lower.endswith((".heic", ".mov")):
                suspicious.append((str(html_file.relative_to(root)), ref))

    report_path = root / "image_audit_report.txt"
    lines: list[str] = []
    lines.append("Image audit report")
    lines.append(f"HTML files scanned: {len(html_files)}")
    lines.append("")

    lines.append(f"Missing references: {len(missing)}")
    for f, ref in missing[:200]:
        lines.append(f"- {f} -> {ref}")
    if len(missing) > 200:
        lines.append(f"... ({len(missing) - 200} more)")

    lines.append("")
    lines.append(f"Non-web-safe references (HEIC/MOV): {len(suspicious)}")
    for f, ref in suspicious[:100]:
        lines.append(f"- {f} -> {ref}")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {report_path.relative_to(root)}")
    print(f"Missing: {len(missing)}")

    # Exit non-zero if missing found (useful for CI, but ok locally)
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
