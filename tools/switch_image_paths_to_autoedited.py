from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


RASTER_EXT_RE = r"(?:jpe?g|png|webp)"


@dataclass(frozen=True)
class RewriteResult:
    file: Path
    replacements: int


def _iter_text_files(root: Path, *, include_exts: set[str], skip_dirs: set[str]) -> list[Path]:
    files: list[Path] = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if any(part in skip_dirs for part in p.parts):
            continue
        if p.suffix.lower() not in include_exts:
            continue
        files.append(p)
    return sorted(files)


def _rewrite_content(content: str) -> tuple[str, int]:
    total = 0

    # 1) Relative/absolute-path references like:
    #    images/foo.webp
    #    ../images/foo.jpg
    #    /images/foo.png
    #    url('images/foo.webp')
    rel_pat = re.compile(
        rf"(?P<prefix>(?:^|[\"'\(=\s]))"
        rf"(?P<lead>(?:/|(?:(?:\./|\.\./)*)))"
        rf"images/(?!logo\.)"  # keep logo.png/logo.webp pointing at images/
        rf"(?P<file>[^\"')\s>]+\.{RASTER_EXT_RE})",
        flags=re.IGNORECASE,
    )

    def _rel_sub(m: re.Match) -> str:
        nonlocal total
        total += 1
        return f"{m.group('prefix')}{m.group('lead')}images_autoedited/{m.group('file')}"

    content = rel_pat.sub(_rel_sub, content)

    # 2) Absolute URL references like:
    #    https://midwestflipllc.com/images/og-image.jpg
    abs_pat = re.compile(
        rf"(?P<base>https?://[^\s\"']+?)"
        rf"/images/(?!logo\.)"  # keep absolute logo.png URLs unchanged
        rf"(?P<file>[^\s\"']+\.{RASTER_EXT_RE})",
        flags=re.IGNORECASE,
    )

    def _abs_sub(m: re.Match) -> str:
        nonlocal total
        total += 1
        return f"{m.group('base')}/images_autoedited/{m.group('file')}"

    content = abs_pat.sub(_abs_sub, content)

    return content, total


def _read_text(path: Path) -> str:
    # Most of this repo is UTF-8; tolerate the occasional odd byte.
    return path.read_text(encoding="utf-8", errors="ignore")


def _write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8", newline="\n")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Switch site references from images/ to images_autoedited/ for raster images (.jpg/.png/.webp)."
    )
    ap.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Site root (default: current working directory)",
    )
    ap.add_argument(
        "--apply",
        action="store_true",
        help="Actually modify files (default is dry-run)",
    )
    ap.add_argument(
        "--backup-suffix",
        type=str,
        default=".bak_imageswitch",
        help="Suffix for backups when --apply is used",
    )
    ap.add_argument(
        "--limit",
        type=int,
        default=30,
        help="How many planned changes to print in dry-run",
    )

    args = ap.parse_args()
    root: Path = args.root
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Root folder not found: {root}")

    # Only touch files that are typically served as part of the static site.
    # Avoid rewriting audit outputs / data files like lighthouse-index.json.
    include_exts = {".html", ".css", ".xml", ".js"}
    skip_dirs = {".git", ".venv", "node_modules", "images", "images_autoedited"}

    candidates = _iter_text_files(root, include_exts=include_exts, skip_dirs=skip_dirs)

    results: list[RewriteResult] = []
    for f in candidates:
        before = _read_text(f)
        after, count = _rewrite_content(before)
        if count and after != before:
            results.append(RewriteResult(file=f, replacements=count))

    if not results:
        print("No changes needed.")
        return 0

    total_repls = sum(r.replacements for r in results)
    print(f"Planned changes: {len(results)} files, {total_repls} replacements")

    if not args.apply:
        for r in results[: max(0, int(args.limit))]:
            print(f"- {r.file.relative_to(root)} ({r.replacements} replacements)")
        if len(results) > args.limit:
            print(f"... ({len(results) - args.limit} more not shown)")
        print("\nDry-run only. Re-run with --apply to write changes.")
        return 0

    # Apply with backups
    for r in results:
        before = _read_text(r.file)
        after, _ = _rewrite_content(before)
        backup_path = r.file.with_name(r.file.name + args.backup_suffix)
        if not backup_path.exists():
            backup_path.write_text(before, encoding="utf-8", newline="\n")
        _write_text(r.file, after)

    print(f"Applied: {len(results)} files updated, backups saved with suffix '{args.backup_suffix}'")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
