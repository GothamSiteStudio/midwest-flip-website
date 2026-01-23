import argparse
import html
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple


TITLE_RE = re.compile(r"(<title[^>]*>)(.*?)(</title>)", flags=re.IGNORECASE | re.DOTALL)


def _normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def _escape_text(text: str) -> str:
    # For <title> content.
    return html.escape(text, quote=False)


def _escape_attr(text: str) -> str:
    # For attribute values.
    return html.escape(text, quote=True)


def _find_and_replace_title(doc: str, new_title: str) -> Tuple[str, bool]:
    m = TITLE_RE.search(doc)
    if not m:
        return doc, False
    replaced = doc[: m.start(2)] + _escape_text(new_title) + doc[m.end(2) :]
    return replaced, True


def _replace_meta_content_by_name(doc: str, name: str, new_content: str) -> Tuple[str, bool]:
    # Finds the first <meta ... name="..." ...> tag and updates/creates its content attribute.
    pat = re.compile(
        r"(<meta\b[^>]*\bname=[\"']" + re.escape(name) + r"[\"'][^>]*>)",
        flags=re.IGNORECASE,
    )
    m = pat.search(doc)
    if not m:
        return doc, False

    tag = m.group(1)
    esc = _escape_attr(new_content)

    if re.search(r"\bcontent\s*=", tag, flags=re.IGNORECASE):
        new_tag = re.sub(
            r"(\bcontent\s*=\s*[\"'])(.*?)([\"'])",
            r"\1" + esc + r"\3",
            tag,
            flags=re.IGNORECASE | re.DOTALL,
            count=1,
        )
    else:
        # Insert content before the closing >
        new_tag = tag[:-1] + f' content="{esc}">'  # safe: tag ends with '>'

    return doc[: m.start(1)] + new_tag + doc[m.end(1) :], True


def _replace_meta_content_by_property(doc: str, prop: str, new_content: str) -> Tuple[str, bool]:
    pat = re.compile(
        r"(<meta\b[^>]*\bproperty=[\"']" + re.escape(prop) + r"[\"'][^>]*>)",
        flags=re.IGNORECASE,
    )
    m = pat.search(doc)
    if not m:
        return doc, False

    tag = m.group(1)
    esc = _escape_attr(new_content)

    if re.search(r"\bcontent\s*=", tag, flags=re.IGNORECASE):
        new_tag = re.sub(
            r"(\bcontent\s*=\s*[\"'])(.*?)([\"'])",
            r"\1" + esc + r"\3",
            tag,
            flags=re.IGNORECASE | re.DOTALL,
            count=1,
        )
    else:
        new_tag = tag[:-1] + f' content="{esc}">'  # safe: tag ends with '>'

    return doc[: m.start(1)] + new_tag + doc[m.end(1) :], True


def _trim_to_word_boundary(text: str, max_len: int) -> str:
    text = _normalize_space(text)
    if len(text) <= max_len:
        return text

    # Prefer to cut at end of sentence within the last 60 chars of the limit.
    window_start = max(0, max_len - 60)
    window = text[window_start:max_len]
    for punct in [". ", "! ", "? ", "; "]:
        idx = window.rfind(punct)
        if idx != -1:
            cut = window_start + idx + 1  # keep punctuation
            return text[:cut].strip()

    # Otherwise cut at last space.
    cut = text.rfind(" ", 0, max_len + 1)
    if cut <= 0:
        return text[:max_len].strip()
    return text[:cut].strip()


def _extend_description(text: str, min_len: int, max_len: int) -> str:
    text = _normalize_space(text)
    if len(text) >= min_len:
        return _trim_to_word_boundary(text, max_len)

    suffixes = [
        "Serving Detroit & Metro Detroit.",
        "Call (313) 389-6324.",
    ]

    for suffix in suffixes:
        candidate = (text + " " + suffix).strip() if text else suffix
        candidate = _normalize_space(candidate)
        if len(candidate) > max_len:
            continue
        text = candidate
        if len(text) >= min_len:
            return text

    # If still short, pad gently without exceeding max.
    extra = "Licensed & insured."
    candidate = _normalize_space((text + " " + extra).strip())
    if len(candidate) <= max_len:
        text = candidate

    return text


def _smart_title(title: str, min_len: int, max_len: int) -> str:
    title = _normalize_space(title)

    # Expand if too short.
    if len(title) < min_len:
        if "midwest flip" not in title.lower():
            title = _normalize_space(f"{title} | Midwest Flip LLC") if title else "Midwest Flip LLC"
        if len(title) < min_len:
            # Add a neutral qualifier.
            add = "Detroit" if "detroit" not in title.lower() else "Michigan"
            candidate = _normalize_space(f"{title} | {add}")
            if len(candidate) <= max_len:
                title = candidate

    # Shorten if too long.
    if len(title) > max_len:
        parts = [p.strip() for p in re.split(r"[|\-–—:]", title) if p.strip()]
        brand = None
        for p in parts:
            if "midwest" in p.lower() and "flip" in p.lower():
                brand = p
                break
        if not brand:
            brand = "Midwest Flip LLC"

        # Candidate descriptors, prefer location and service keywords.
        keywords = ["detroit", "metro detroit", "remodel", "contractor", "builder", "services"]
        descriptors = [p for p in parts if p != brand]
        descriptors_sorted = sorted(
            descriptors,
            key=lambda p: (
                -sum(1 for k in keywords if k in p.lower()),
                len(p),
            ),
        )

        candidate_parts = [brand]
        for p in descriptors_sorted:
            cand = " | ".join(candidate_parts + [p])
            if len(cand) <= max_len:
                candidate_parts.append(p)
            if len(" | ".join(candidate_parts)) >= min_len:
                break

        title = " | ".join(candidate_parts)

        if len(title) > max_len:
            title = _trim_to_word_boundary(title, max_len)

    # Final clamp.
    title = _trim_to_word_boundary(title, max_len)
    if len(title) < min_len:
        # Worst-case fallback.
        fallback = "Midwest Flip LLC | Detroit Home Remodeling"
        if min_len <= len(fallback) <= max_len:
            return fallback
    return title


@dataclass
class FixResult:
    file: Path
    changed: bool
    old_title: Optional[str]
    new_title: Optional[str]
    old_desc: Optional[str]
    new_desc: Optional[str]


def _extract_title(doc: str) -> Optional[str]:
    m = TITLE_RE.search(doc)
    if not m:
        return None
    return _normalize_space(html.unescape(m.group(2)))


def _extract_meta_description(doc: str) -> Optional[str]:
    m = re.search(
        r"<meta\b[^>]*\bname=[\"']description[\"'][^>]*>", doc, flags=re.IGNORECASE
    )
    if not m:
        return None
    tag = m.group(0)
    m2 = re.search(r"\bcontent\s*=\s*[\"'](.*?)[\"']", tag, flags=re.IGNORECASE | re.DOTALL)
    if not m2:
        return None
    return _normalize_space(html.unescape(m2.group(1)))


def fix_file(
    file_path: Path,
    title_min: int,
    title_max: int,
    desc_min: int,
    desc_max: int,
    update_og: bool,
    update_twitter: bool,
) -> FixResult:
    doc = file_path.read_text(encoding="utf-8", errors="replace")
    old_title = _extract_title(doc)
    old_desc = _extract_meta_description(doc)

    changed = False
    new_title = old_title
    new_desc = old_desc

    if old_title is not None:
        t2 = _smart_title(old_title, title_min, title_max)
        if t2 != old_title:
            doc, ok = _find_and_replace_title(doc, t2)
            if ok:
                changed = True
                new_title = t2

    if old_desc is not None:
        d2 = old_desc
        if len(d2) > desc_max:
            d2 = _trim_to_word_boundary(d2, desc_max)
        if len(d2) < desc_min:
            d2 = _extend_description(d2, desc_min, desc_max)
        d2 = _trim_to_word_boundary(d2, desc_max)
        if d2 != old_desc:
            doc, ok = _replace_meta_content_by_name(doc, "description", d2)
            if ok:
                changed = True
                new_desc = d2

    # Keep OG/Twitter in sync when requested and when we have values.
    if update_og:
        if new_title:
            doc2, ok = _replace_meta_content_by_property(doc, "og:title", new_title)
            if ok:
                doc = doc2
                changed = True
        if new_desc:
            doc2, ok = _replace_meta_content_by_property(doc, "og:description", new_desc)
            if ok:
                doc = doc2
                changed = True

    if update_twitter:
        if new_title:
            doc2, ok = _replace_meta_content_by_name(doc, "twitter:title", new_title)
            if ok:
                doc = doc2
                changed = True
        if new_desc:
            doc2, ok = _replace_meta_content_by_name(doc, "twitter:description", new_desc)
            if ok:
                doc = doc2
                changed = True

    if changed:
        file_path.write_text(doc, encoding="utf-8")

    return FixResult(
        file=file_path,
        changed=changed,
        old_title=old_title,
        new_title=new_title,
        old_desc=old_desc,
        new_desc=new_desc,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fix Title + Meta Description lengths based on the latest seo_audit_report.json",
    )
    parser.add_argument("--root", default=".", help="Site root folder (default: current directory).")
    parser.add_argument(
        "--report",
        default="seo_audit_report.json",
        help="SEO audit JSON report path (relative to root).",
    )
    parser.add_argument("--title-min", type=int, default=30)
    parser.add_argument("--title-max", type=int, default=60)
    parser.add_argument("--desc-min", type=int, default=70)
    parser.add_argument("--desc-max", type=int, default=160)
    parser.add_argument(
        "--update-og",
        action="store_true",
        help="Also update og:title/og:description if present.",
    )
    parser.add_argument(
        "--update-twitter",
        action="store_true",
        help="Also update twitter:title/twitter:description if present.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute changes but do not write files.",
    )

    args = parser.parse_args()

    root = Path(args.root).resolve()
    report_path = (root / args.report).resolve()
    data = json.loads(report_path.read_text(encoding="utf-8"))

    pages = data.get("pages", [])
    target_files: List[Path] = []
    for p in pages:
        if p.get("warnings") or p.get("errors"):
            rel = p.get("file")
            if rel:
                target_files.append(root / rel)

    # Dedupe
    seen: set[Path] = set()
    files: List[Path] = []
    for f in target_files:
        if f in seen:
            continue
        seen.add(f)
        files.append(f)

    results: List[FixResult] = []
    for f in files:
        if not f.exists() or not f.is_file():
            continue
        if args.dry_run:
            # Run fix but prevent writes.
            before = f.read_text(encoding="utf-8", errors="replace")
            res = fix_file(
                f,
                title_min=args.title_min,
                title_max=args.title_max,
                desc_min=args.desc_min,
                desc_max=args.desc_max,
                update_og=args.update_og,
                update_twitter=args.update_twitter,
            )
            # Restore
            f.write_text(before, encoding="utf-8")
            results.append(res)
        else:
            results.append(
                fix_file(
                    f,
                    title_min=args.title_min,
                    title_max=args.title_max,
                    desc_min=args.desc_min,
                    desc_max=args.desc_max,
                    update_og=args.update_og,
                    update_twitter=args.update_twitter,
                )
            )

    changed = [r for r in results if r.changed]

    print("SEO fix complete")
    print(f"Files considered: {len(results)}")
    print(f"Files changed:    {len(changed)}")

    # Print a small sample for confidence.
    for r in changed[:12]:
        print(f"- {r.file.relative_to(root).as_posix()}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
