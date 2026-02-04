from __future__ import annotations

from pathlib import Path
from typing import Iterable


MATOMO_SNIPPET = """<!-- Matomo -->
<script>
  var _paq = window._paq = window._paq || [];
  /* tracker methods like \"setCustomDimension\" should be called before \"trackPageView\" */
  _paq.push(['trackPageView']);
  _paq.push(['enableLinkTracking']);
  (function() {
    var u=\"https://alphalockandsafe.matomo.cloud/\";
    _paq.push(['setTrackerUrl', u+'matomo.php']);
    _paq.push(['setSiteId', '2']);
    var d=document, g=d.createElement('script'), s=d.getElementsByTagName('script')[0];
    g.async=true; g.src='https://cdn.matomo.cloud/alphalockandsafe.matomo.cloud/matomo.js'; s.parentNode.insertBefore(g,s);
  })();
</script>
<!-- End Matomo Code -->"""


def iter_html_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*.html"):
        if path.is_file():
            yield path


def has_matomo(content: str) -> bool:
    return "matomo.cloud/alphalockandsafe.matomo.cloud" in content or "Matomo" in content


def insert_before_head_close(content: str) -> str | None:
    head_close = "</head>"
    if head_close not in content:
        return None
    if has_matomo(content):
        return None

    insert_at = content.lower().rfind(head_close)
    if insert_at == -1:
        return None

    before = content[:insert_at]
    after = content[insert_at:]

    spacer = "\n" if not before.endswith("\n") else ""
    return f"{before}{spacer}{MATOMO_SNIPPET}\n{after}"


def process_file(path: Path) -> bool:
    content = path.read_text(encoding="utf-8", errors="ignore")
    updated = insert_before_head_close(content)
    if updated is None:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def main() -> None:
    root = Path(__file__).resolve().parent
    changed = 0
    for html_path in iter_html_files(root):
        if process_file(html_path):
            changed += 1
    print(f"Matomo snippet added to {changed} file(s).")


if __name__ == "__main__":
    main()
