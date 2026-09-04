from __future__ import annotations

from .catalog import MaterialCatalog


class MaterialSearch:
    def __init__(self, catalog: MaterialCatalog) -> None:
        self.catalog = catalog

    def search(self, query: str, *, media_type: str | None = None, limit: int = 20) -> list[dict[str, object]]:
        terms = [term.casefold() for term in query.split() if term]
        if not terms:
            return []
        results = []
        for segment in self.catalog.segments.values():
            resource = self.catalog.resources[segment.resource_id]
            if media_type and resource.media_type != media_type:
                continue
            haystack = f"{segment.filename}\n{segment.section or ''}\n{segment.text}".casefold()
            matches = sum(haystack.count(term) for term in terms)
            if matches:
                item = segment.as_dict()
                item["snippet"] = _snippet(segment.text, terms)
                item.pop("text", None)
                item["match_score"] = matches
                results.append(item)
        results.sort(key=lambda item: (-int(item["match_score"]), str(item["filename"]), str(item["citation_anchor"])))
        return results[: max(0, limit)]


def _snippet(text: str, terms: list[str], radius: int = 80) -> str:
    """Return a bounded, whitespace-normalized excerpt around the first hit."""
    compact = " ".join(text.split())
    folded = compact.casefold()
    positions = [folded.find(term) for term in terms if folded.find(term) >= 0]
    if not positions:
        return compact[: radius * 2]
    hit = min(positions)
    start = max(0, hit - radius)
    end = min(len(compact), hit + radius)
    prefix = "…" if start else ""
    suffix = "…" if end < len(compact) else ""
    return f"{prefix}{compact[start:end]}{suffix}"
