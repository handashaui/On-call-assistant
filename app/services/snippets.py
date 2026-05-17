import html
import re


def highlighted_snippet(text: str, query: str, radius: int = 80) -> str:
    if not text:
        return ""

    match = _find_match(text, query)
    if not match:
        return html.escape(text[: radius * 2].strip())

    start = max(match.start() - radius, 0)
    end = min(match.end() + radius, len(text))
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(text) else ""
    return f"{prefix}{highlight_terms(text[start:end].strip(), query)}{suffix}"


def highlight_terms(text: str, query: str) -> str:
    if not query:
        return html.escape(text)

    pattern = re.compile(re.escape(query), flags=re.IGNORECASE)
    pieces: list[str] = []
    cursor = 0
    for match in pattern.finditer(text):
        pieces.append(html.escape(text[cursor : match.start()]))
        pieces.append(f"<mark>{html.escape(match.group(0))}</mark>")
        cursor = match.end()
    pieces.append(html.escape(text[cursor:]))
    return "".join(pieces)


def _find_match(text: str, query: str):
    if not query:
        return None
    return re.search(re.escape(query), text, flags=re.IGNORECASE)
