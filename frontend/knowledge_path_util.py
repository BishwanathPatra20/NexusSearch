from pathlib import Path
from typing import Any, Dict, List, Optional

_KIND_ICON = {
    "root": "📚",
    "repository": "🗂️",
    "source": "📥",
    "folder": "📁",
    "ellipsis": "…",
    "file": "📄",
    "page": "📑",
    "section": "§",
    "chunk": "✅",
}


def _shorten_parts(parts: List[str], max_segments: int = 5) -> List[str]:
    if len(parts) <= max_segments:
        return parts
    return [parts[0], "…", *parts[-(max_segments - 2) :]]


def humanize_path_label(node: Dict[str, Any]) -> str:
    """Plain-language labels for business / non-technical users."""
    kind = node.get("kind", "")
    label = node.get("label", "") or ""

    if kind == "root":
        return "Governed library"
    if kind == "repository":
        if label.startswith("store/"):
            doc_id = label.split("/")[-1]
            return f"Indexed document #{doc_id}"
        if label.startswith("Indexed document"):
            return label
    if kind == "source" and label == "Uploads":
        return "Uploaded into NexusSearch"
    if kind == "source" and label == "Folder ingest":
        return "Imported from a folder"
    if kind == "folder":
        return label if label != "…" else "…"
    if kind == "file":
        stem = Path(label).stem.replace("_", " ").replace("-", " ")
        return stem[:48] + ("…" if len(stem) > 48 else "")
    if kind == "page":
        return label
    if kind == "section":
        return f'Section "{label}"' if label else "Section"
    if kind == "chunk" or label.startswith("Chunk"):
        return "Matching excerpt (this result)"
    return label


def path_summary_sentence(nodes: List[Dict[str, Any]]) -> str:
    if not nodes:
        return ""
    human = [humanize_path_label(n) for n in nodes]
    active = next((n for n in nodes if n.get("active")), nodes[-1] if nodes else None)
    where = humanize_path_label(active) if active else human[-1]
    if len(human) <= 2:
        return f"This result comes from **{where}** in your governed library."
    mid = " → ".join(human[1:-1])
    return f"**Path:** Governed library → {mid} → **{where}**"


def nodes_for_display(nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for node in nodes:
        copy = dict(node)
        copy["label"] = humanize_path_label(node)
        copy["icon"] = _KIND_ICON.get(node.get("kind", ""), "•")
        out.append(copy)
    return out


def build_knowledge_path(
    *,
    source_type: str,
    source_uri: Optional[str],
    file_name: str,
    document_id: int,
    page_number: Optional[int] = None,
    chunk_index: Optional[int] = None,
    chunk_id: Optional[int] = None,
    section: Optional[str] = None,
) -> List[Dict[str, Any]]:
    nodes: List[Dict[str, Any]] = [
        {"key": "vault", "label": "Knowledge Vault", "kind": "root", "active": False},
        {"key": "store", "label": f"store/{document_id}", "kind": "repository", "active": False},
    ]

    if source_type == "folder" and source_uri:
        nodes.append({"key": "ingest", "label": "Folder ingest", "kind": "source", "active": False})
        path = Path(source_uri).expanduser()
        parts = [p for p in path.parts if p]
        if parts and parts[0] == "/":
            parts = parts[1:]
        if parts and parts[0] == "Users" and len(parts) >= 2:
            parts = ["~", *parts[2:]]
        dir_parts = parts[:-1] if parts else []
        for idx, segment in enumerate(_shorten_parts(dir_parts)):
            nodes.append(
                {
                    "key": f"dir-{idx}",
                    "label": segment,
                    "kind": "folder" if segment != "…" else "ellipsis",
                    "active": False,
                }
            )
        leaf = parts[-1] if parts else file_name
        nodes.append({"key": "file", "label": leaf, "kind": "file", "active": False})
    else:
        nodes.append({"key": "uploads", "label": "Uploads", "kind": "source", "active": False})
        nodes.append({"key": "file", "label": file_name, "kind": "file", "active": False})

    if page_number is not None:
        nodes.append({"key": "page", "label": f"Page {page_number}", "kind": "page", "active": False})
    if section:
        short = section if len(section) <= 40 else section[:37] + "…"
        nodes.append({"key": "section", "label": short, "kind": "section", "active": False})
    if chunk_index is not None or chunk_id is not None:
        suffix = f"#{chunk_index}" if chunk_index is not None else ""
        label = f"Chunk {chunk_id}" if chunk_id else f"Chunk{suffix}"
        nodes.append({"key": "chunk", "label": label, "kind": "chunk", "active": True})
    elif nodes:
        nodes[-1]["active"] = True

    return nodes
