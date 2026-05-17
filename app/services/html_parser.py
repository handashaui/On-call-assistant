import re

from bs4 import BeautifulSoup

from app.schemas.document import Document, Section


_SPACE_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    return _SPACE_RE.sub(" ", text).strip()


def parse_html_document(doc_id: str, html: str, filename: str | None = None) -> Document:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript", "template"]):
        tag.decompose()

    title = ""
    if soup.title and soup.title.get_text(strip=True):
        title = soup.title.get_text(" ", strip=True)
    elif soup.find("h1"):
        title = soup.find("h1").get_text(" ", strip=True)
    else:
        title = doc_id

    h1_tag = soup.find("h1")
    h1 = normalize_text(h1_tag.get_text(" ", strip=True)) if h1_tag else None

    metadata_text = _extract_metadata_text(soup)
    content_root = _content_root(soup)
    h2_headings, h3_headings, sections = _extract_sections(content_root)
    body = normalize_text(" ".join(section.content for section in sections))

    if not body:
        body = normalize_text(content_root.get_text(" ", strip=True))

    text = normalize_text(
        " ".join(
            [
                title,
                h1 or "",
                metadata_text,
                " ".join(h2_headings),
                " ".join(h3_headings),
                body,
            ]
        )
    )

    return Document(
        id=doc_id,
        title=normalize_text(title),
        h1=h1,
        metadata_text=metadata_text,
        h2_headings=h2_headings,
        h3_headings=h3_headings,
        sections=sections,
        body=body,
        text=text,
        html=html,
        filename=filename,
    )


def _extract_metadata_text(soup: BeautifulSoup) -> str:
    header = soup.find("header")
    if not header:
        return ""
    return normalize_text(" ".join(p.get_text(" ", strip=True) for p in header.find_all("p")))


def _content_root(soup: BeautifulSoup):
    return (
        soup.find("main")
        or soup.select_one("article.main-content")
        or soup.select_one("section.content-section")
        or soup.body
        or soup
    )


def _extract_sections(root) -> tuple[list[str], list[str], list[Section]]:
    h2_headings: list[str] = []
    h3_headings: list[str] = []
    sections: list[Section] = []
    current_heading: str | None = None
    current_level: int | None = None
    current_parts: list[str] = []

    def flush_section() -> None:
        nonlocal current_heading, current_level, current_parts
        content = normalize_text(" ".join(current_parts))
        if current_heading and current_level and content:
            sections.append(Section(heading=current_heading, level=current_level, content=content))
        current_heading = None
        current_level = None
        current_parts = []

    for node in root.find_all(["h2", "h3", "p", "li"], recursive=True):
        text = normalize_text(node.get_text(" ", strip=True))
        if not text:
            continue

        if node.name in {"h2", "h3"}:
            flush_section()
            current_heading = text
            current_level = 2 if node.name == "h2" else 3
            if node.name == "h2":
                h2_headings.append(text)
            else:
                h3_headings.append(text)
            continue

        if current_heading:
            current_parts.append(text)

    flush_section()
    return h2_headings, h3_headings, sections
