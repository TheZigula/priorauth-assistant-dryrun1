# docs/build_pdf.py: owned by instance 4 (docs). Turns docs/one_pager.md into docs/one_pager.pdf with only the
# standard library (the small Markdown subset the page uses, to HTML) and Microsoft Edge's headless print-to-PDF.
import html
import re
import subprocess
import sys
import tempfile
from pathlib import Path

DOCS = Path(__file__).resolve().parent
SRC = DOCS / "one_pager.md"
OUT = DOCS / "one_pager.pdf"
EDGE_CANDIDATES = [
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
]

CSS = """
@page { size: Letter; margin: 0.6in 0.7in; }
body { font-family: "Segoe UI", Arial, sans-serif; font-size: 10.5pt; line-height: 1.4; color: #1f2328; }
h1 { font-size: 18pt; margin: 0 0 10pt; color: #0b3d5c; }
h2 { font-size: 13pt; margin: 12pt 0 4pt; color: #0b3d5c; border-bottom: 1px solid #d0d7de; padding-bottom: 2pt; }
p, li { margin: 0 0 4pt; }
ul, ol { margin: 0 0 4pt; padding-left: 18pt; }
"""


def inline(text: str) -> str:
    text = html.escape(text, quote=False)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)


def to_html(md: str) -> tuple[str, str]:
    """Return (title, body html) for headings, paragraphs, bullet lists, numbered lists and **bold**."""
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)  # the header comment is for the repo, not the reader
    out: list[str] = []
    para: list[str] = []
    list_tag = None
    title = ""

    def flush_para() -> None:
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")
            para.clear()

    def close_list() -> None:
        nonlocal list_tag
        if list_tag:
            out.append(f"</{list_tag}>")
            list_tag = None

    for line in md.splitlines():
        s = line.strip()
        bullet = re.match(r"^- (.*)", s)
        numbered = re.match(r"^\d+\. (.*)", s)
        if not s:
            flush_para()
            close_list()
        elif s.startswith("#"):
            flush_para()
            close_list()
            level = len(s) - len(s.lstrip("#"))
            text = s[level:].strip()
            title = title or text
            out.append(f"<h{level}>{inline(text)}</h{level}>")
        elif bullet or numbered:
            flush_para()
            tag = "ul" if bullet else "ol"
            if list_tag != tag:
                close_list()
                out.append(f"<{tag}>")
                list_tag = tag
            out.append(f"<li>{inline((bullet or numbered).group(1))}</li>")
        else:
            para.append(s)
    flush_para()
    close_list()
    return title, "\n".join(out)


def main() -> int:
    edge = next((p for p in EDGE_CANDIDATES if p.exists()), None)
    if edge is None:
        print("Microsoft Edge was not found, so the PDF cannot be printed.", file=sys.stderr)
        return 1
    title, body = to_html(SRC.read_text(encoding="utf-8"))
    page = (
        f"<!doctype html><html lang='en'><head><meta charset='utf-8'><title>{html.escape(title)}</title>"
        f"<style>{CSS}</style></head><body>{body}</body></html>"
    )
    with tempfile.TemporaryDirectory() as tmp:
        src_html = Path(tmp) / "one_pager.html"
        src_html.write_text(page, encoding="utf-8")
        # A throwaway profile, so the print never touches or waits on the Edge window you have open.
        subprocess.run(
            [str(edge), "--headless", "--disable-gpu", "--no-first-run", "--no-pdf-header-footer",
             f"--user-data-dir={Path(tmp) / 'edge-profile'}", f"--print-to-pdf={OUT}", src_html.as_uri()],
            check=True, timeout=120, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    if not OUT.exists() or OUT.stat().st_size == 0:
        print("Edge ran but wrote no PDF.", file=sys.stderr)
        return 1
    pages = len(re.findall(rb"/Type\s*/Page[^s]", OUT.read_bytes()))
    print(f"wrote {OUT.relative_to(DOCS.parent)}: {OUT.stat().st_size} bytes, {pages} page(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
