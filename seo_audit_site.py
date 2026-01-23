import argparse
import csv
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Optional

from bs4 import BeautifulSoup


DEFAULT_EXCLUDE_DIRS = {".git", ".venv", "node_modules", "dist", "build"}


def _str_list() -> list[str]:
    return []


@dataclass
class ImageAltFinding:
    src: str
    alt: Optional[str]


def _image_alt_finding_list() -> list[ImageAltFinding]:
    return []


@dataclass
class PageAudit:
    file: str
    url: Optional[str]

    title: Optional[str]
    title_length: int
    title_ok: bool

    meta_description: Optional[str]
    meta_description_length: int
    meta_description_ok: bool

    h1_count: int
    h2_count: int
    headings_order_warnings: list[str] = field(default_factory=_str_list)

    images_count: int = 0
    images_missing_alt_count: int = 0
    images_empty_alt_count: int = 0
    images_missing_alt_samples: list[ImageAltFinding] = field(default_factory=_image_alt_finding_list)

    errors: list[str] = field(default_factory=_str_list)
    warnings: list[str] = field(default_factory=_str_list)


def _normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _get_meta_content(soup: BeautifulSoup, name: str) -> Optional[str]:
    tag = soup.find("meta", attrs={"name": name})
    if not tag:
        return None
    content = tag.get("content")
    if content is None:
        return None
    content = _normalize_space(str(content))
    return content or None


def _get_title(soup: BeautifulSoup) -> Optional[str]:
    if soup.title and soup.title.string is not None:
        return _normalize_space(soup.title.string)
    tag = soup.find("title")
    if not tag:
        return None
    return _normalize_space(tag.get_text(" ", strip=True)) or None


def _check_h1_h2_order(soup: BeautifulSoup) -> list[str]:
    """Checks simple H1/H2 structure as requested.

    - H1 should appear before any H2.
    - H2 is optional, but if present before H1 it's a warning.
    """
    warnings: list[str] = []
    headings = soup.find_all(["h1", "h2"])
    if not headings:
        return ["No H1/H2 headings found."]

    first = headings[0].name.lower() if getattr(headings[0], "name", None) else ""
    if first == "h2" and soup.find("h1") is not None:
        warnings.append("H2 appears before H1.")

    return warnings


def _is_decorative_image(img_tag: Any) -> bool:
    role = (img_tag.get("role") or "").strip().lower()
    aria_hidden = (img_tag.get("aria-hidden") or "").strip().lower()
    if role == "presentation":
        return True
    if aria_hidden in {"true", "1"}:
        return True
    return False


def _make_url(base_url: Optional[str], rel_path: str) -> Optional[str]:
    if not base_url:
        return None
    base = base_url.rstrip("/")
    rel = rel_path.replace("\\", "/").lstrip("/")
    return f"{base}/{rel}"


def audit_html_file(
    file_path: Path,
    site_root: Path,
    base_url: Optional[str],
    title_min: int,
    title_max: int,
    description_min: int,
    description_max: int,
    max_image_samples: int,
) -> PageAudit:
    rel_path = file_path.relative_to(site_root).as_posix()

    html = file_path.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(html, "lxml")

    title = _get_title(soup)
    title_len = len(title) if title else 0
    title_ok = bool(title) and title_min <= title_len <= title_max

    description = _get_meta_content(soup, "description")
    desc_len = len(description) if description else 0
    desc_ok = bool(description) and description_min <= desc_len <= description_max

    h1_count = len(soup.find_all("h1"))
    h2_count = len(soup.find_all("h2"))

    heading_order_warnings = _check_h1_h2_order(soup)

    images = soup.find_all("img")
    images_count = len(images)

    missing_alt: list[ImageAltFinding] = []
    empty_alt_count = 0
    missing_alt_count = 0

    for img in images:
        if _is_decorative_image(img):
            continue
        src = _normalize_space(str(img.get("src") or ""))
        alt = img.get("alt")
        if alt is None:
            missing_alt_count += 1
            if len(missing_alt) < max_image_samples:
                missing_alt.append(ImageAltFinding(src=src, alt=None))
            continue
        alt_norm = _normalize_space(str(alt))
        if alt_norm == "":
            empty_alt_count += 1

    audit = PageAudit(
        file=rel_path,
        url=_make_url(base_url, rel_path),
        title=title,
        title_length=title_len,
        title_ok=title_ok,
        meta_description=description,
        meta_description_length=desc_len,
        meta_description_ok=desc_ok,
        h1_count=h1_count,
        h2_count=h2_count,
        headings_order_warnings=heading_order_warnings,
        images_count=images_count,
        images_missing_alt_count=missing_alt_count,
        images_empty_alt_count=empty_alt_count,
        images_missing_alt_samples=missing_alt,
    )

    # Errors / warnings
    if not title:
        audit.errors.append("Missing <title>.")
    elif not title_ok:
        audit.warnings.append(
            f"Title length {title_len} outside recommended range {title_min}-{title_max}."
        )

    if not description:
        audit.errors.append('Missing meta description (<meta name="description">).')
    elif not desc_ok:
        audit.warnings.append(
            f"Meta description length {desc_len} outside recommended range {description_min}-{description_max}."
        )

    if h1_count == 0:
        audit.errors.append("Missing H1.")
    elif h1_count > 1:
        audit.warnings.append(f"Multiple H1 tags ({h1_count}).")

    # If H2 exists but no H1, it's already an error; otherwise just let order warnings show.
    if heading_order_warnings:
        audit.warnings.extend(heading_order_warnings)

    if missing_alt_count > 0:
        audit.errors.append(f"{missing_alt_count} image(s) missing alt attribute.")
    if empty_alt_count > 0:
        audit.warnings.append(f"{empty_alt_count} image(s) have empty alt (alt=\"\").")

    return audit


def iter_html_files(site_root: Path, exclude_dirs: Iterable[str]) -> list[Path]:
    exclude = {d.lower() for d in exclude_dirs}
    files: list[Path] = []
    for path in site_root.rglob("*.html"):
        if not path.is_file():
            continue
        parts_lower = {p.lower() for p in path.relative_to(site_root).parts}
        if parts_lower & exclude:
            continue
        files.append(path)
    return sorted(files)


def write_csv(out_path: Path, audits: list[PageAudit]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "file",
                "url",
                "title_length",
                "title_ok",
                "meta_description_length",
                "meta_description_ok",
                "h1_count",
                "h2_count",
                "images_count",
                "images_missing_alt_count",
                "images_empty_alt_count",
                "errors_count",
                "warnings_count",
            ],
        )
        writer.writeheader()
        for a in audits:
            writer.writerow(
                {
                    "file": a.file,
                    "url": a.url or "",
                    "title_length": a.title_length,
                    "title_ok": a.title_ok,
                    "meta_description_length": a.meta_description_length,
                    "meta_description_ok": a.meta_description_ok,
                    "h1_count": a.h1_count,
                    "h2_count": a.h2_count,
                    "images_count": a.images_count,
                    "images_missing_alt_count": a.images_missing_alt_count,
                    "images_empty_alt_count": a.images_empty_alt_count,
                    "errors_count": len(a.errors),
                    "warnings_count": len(a.warnings),
                }
            )


def summarize(audits: list[PageAudit]) -> dict[str, Any]:
    pages = len(audits)
    pages_with_errors = sum(1 for a in audits if a.errors)
    pages_with_warnings = sum(1 for a in audits if a.warnings)

    issue_counts: dict[str, int] = {}
    for a in audits:
        for e in a.errors:
            issue_counts[e] = issue_counts.get(e, 0) + 1
        for w in a.warnings:
            issue_counts[w] = issue_counts.get(w, 0) + 1

    top_issues = sorted(issue_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:20]

    return {
        "pages": pages,
        "pages_with_errors": pages_with_errors,
        "pages_with_warnings": pages_with_warnings,
        "top_issues": [{"issue": k, "count": v} for k, v in top_issues],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "SEO audit for local static HTML files: Title length, meta description, H1/H2 order, and image alt."\
        )
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Site root folder to scan (default: current directory).",
    )
    parser.add_argument(
        "--base-url",
        default="",
        help="Optional base URL (used to show URLs in the report).",
    )
    parser.add_argument(
        "--out-json",
        default="seo_audit_report.json",
        help="Output JSON report path (relative to root).",
    )
    parser.add_argument(
        "--out-csv",
        default="seo_audit_report.csv",
        help="Output CSV report path (relative to root).",
    )
    parser.add_argument(
        "--title-min",
        type=int,
        default=30,
        help="Recommended minimum title length.",
    )
    parser.add_argument(
        "--title-max",
        type=int,
        default=60,
        help="Recommended maximum title length.",
    )
    parser.add_argument(
        "--desc-min",
        type=int,
        default=70,
        help="Recommended minimum meta description length.",
    )
    parser.add_argument(
        "--desc-max",
        type=int,
        default=160,
        help="Recommended maximum meta description length.",
    )
    parser.add_argument(
        "--exclude-dir",
        action="append",
        default=[],
        help=(
            "Directory name to exclude (can be provided multiple times). "
            f"Default excludes: {', '.join(sorted(DEFAULT_EXCLUDE_DIRS))}."
        ),
    )
    parser.add_argument(
        "--max-image-samples",
        type=int,
        default=10,
        help="Max sample image entries per page for missing alt.",
    )

    args = parser.parse_args()

    site_root = Path(args.root).resolve()
    base_url = args.base_url.strip() or None

    exclude_dirs = list(DEFAULT_EXCLUDE_DIRS) + list(args.exclude_dir or [])
    html_files = iter_html_files(site_root, exclude_dirs)

    audits: list[PageAudit] = []
    for f in html_files:
        audits.append(
            audit_html_file(
                f,
                site_root=site_root,
                base_url=base_url,
                title_min=args.title_min,
                title_max=args.title_max,
                description_min=args.desc_min,
                description_max=args.desc_max,
                max_image_samples=args.max_image_samples,
            )
        )

    summary = summarize(audits)

    out_json = (site_root / args.out_json).resolve()
    out_csv = (site_root / args.out_csv).resolve()

    out_json.write_text(
        json.dumps(
            {
                "root": str(site_root),
                "base_url": base_url,
                "summary": summary,
                "pages": [asdict(a) for a in audits],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    write_csv(out_csv, audits)

    print("SEO audit complete")
    print(f"Pages scanned: {summary['pages']}")
    print(f"Pages with errors: {summary['pages_with_errors']}")
    print(f"Pages with warnings: {summary['pages_with_warnings']}")
    print(f"JSON report: {out_json}")
    print(f"CSV report:  {out_csv}")

    if summary["top_issues"]:
        print("\nTop issues:")
        for item in summary["top_issues"][:10]:
            print(f"- {item['count']}x {item['issue']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
