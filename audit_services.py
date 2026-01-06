import argparse
import difflib
import html as html_lib
import re
from pathlib import Path


def extract_h4_titles(services_html: str) -> list[str]:
    raw_titles = re.findall(r"<h4>(.*?)</h4>", services_html, flags=re.IGNORECASE | re.DOTALL)
    return [html_lib.unescape(re.sub(r"\s+", " ", t)).strip() for t in raw_titles]


def normalize(text: str) -> str:
    text = html_lib.unescape(text)
    text = text.lower().strip()
    text = re.sub(r"&", " and ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_source_services(source_text: str) -> list[str]:
    services: list[str] = []

    for line in source_text.splitlines():
        raw = line.strip()
        if not raw:
            continue

        # Accept common bullet formats.
        m = re.match(r"^(?:[-*•]|\d+\)|\d+\.|\d+\s+-)\s+(.*)$", raw)
        if m:
            item = m.group(1).strip()
            if item:
                services.append(item)
            continue

        # If the user pastes a plain list (one service per line), allow it too.
        # We skip obvious section headers.
        if len(raw) < 80 and raw.endswith(":"):
            continue
        if raw.startswith("#"):
            continue

        services.append(raw)

    # De-dupe while preserving order.
    seen: set[str] = set()
    out: list[str] = []
    for s in services:
        key = normalize(s)
        if key and key not in seen:
            seen.add(key)
            out.append(s)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Audit services.html against a source list. "
            "Provide a text file with one service per line (bullets supported)."
        )
    )
    parser.add_argument("--services-html", default="services.html", help="Path to services.html")
    parser.add_argument(
        "--source", default="services_source.txt", help="Path to source services list text file"
    )
    parser.add_argument("--max-suggestions", type=int, default=3, help="Suggestions per missing item")
    args = parser.parse_args()

    services_html_path = Path(args.services_html)
    source_path = Path(args.source)

    services_html = services_html_path.read_text(encoding="utf-8", errors="replace")
    source_text = source_path.read_text(encoding="utf-8", errors="replace")

    html_titles = extract_h4_titles(services_html)
    html_norm_to_title: dict[str, str] = {}
    for t in html_titles:
        k = normalize(t)
        if k and k not in html_norm_to_title:
            html_norm_to_title[k] = t

    source_services = extract_source_services(source_text)

    missing: list[str] = []
    matched: int = 0

    html_norm_keys = set(html_norm_to_title.keys())

    for s in source_services:
        k = normalize(s)
        if not k:
            continue
        if k in html_norm_keys:
            matched += 1
        else:
            missing.append(s)

    print(f"services.html H4 count: {len(html_titles)}")
    print(f"Source service lines: {len(source_services)}")
    print(f"Matched: {matched}")
    print(f"Missing: {len(missing)}")

    if missing:
        print("\nMissing items (with suggestions):")
        html_display = list(html_norm_to_title.values())
        for s in missing:
            candidates = difflib.get_close_matches(s, html_display, n=args.max_suggestions, cutoff=0.6)
            if candidates:
                print(f"- {s}  ->  maybe: {', '.join(candidates)}")
            else:
                print(f"- {s}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
