from pathlib import Path
from typing import List, Optional

from backend.app.integrations.confluence_url import parse_page_id_from_source_uri
from backend.app.schemas.models import KnowledgePathNode


def _shorten_parts(parts: List[str], max_segments: int = 5) -> List[str]:
    if len(parts) <= max_segments:
        return parts
    head = parts[0]
    tail = parts[-(max_segments - 2) :]
    return [head, "…", *tail]


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
) -> List[KnowledgePathNode]:
    """Build root → storage → document → in-document location for UI graph."""
    nodes: List[KnowledgePathNode] = [
        KnowledgePathNode(key="vault", label="Governed library", kind="root"),
    ]

    nodes.append(
        KnowledgePathNode(
            key="store",
            label=f"Indexed document #{document_id}",
            kind="repository",
        )
    )

    if source_type == "confluence":
        page_id = parse_page_id_from_source_uri(source_uri)
        wiki_label = f"Confluence page {page_id}" if page_id else "Confluence (live sync)"
        nodes.append(KnowledgePathNode(key="confluence", label=wiki_label, kind="source"))
        nodes.append(KnowledgePathNode(key="file", label=file_name, kind="file"))
    elif source_type == "folder" and source_uri:
        nodes.append(
            KnowledgePathNode(key="ingest", label="Imported from folder", kind="source")
        )
        path = Path(source_uri).expanduser()
        parts = [p for p in path.parts if p]
        if parts and parts[0] == "/":
            parts = parts[1:]
        if parts and parts[0] == "Users" and len(parts) >= 2:
            parts = ["~", *parts[2:]]
        dir_parts = parts[:-1] if parts else []
        for idx, segment in enumerate(_shorten_parts(dir_parts)):
            nodes.append(
                KnowledgePathNode(
                    key=f"dir-{idx}",
                    label=segment,
                    kind="folder" if segment != "…" else "ellipsis",
                )
            )
        leaf = parts[-1] if parts else file_name
        nodes.append(KnowledgePathNode(key="file", label=leaf, kind="file"))
    else:
        nodes.append(
            KnowledgePathNode(key="uploads", label="Uploaded into NexusSearch", kind="source")
        )
        nodes.append(KnowledgePathNode(key="file", label=file_name, kind="file"))

    if page_number is not None:
        nodes.append(
            KnowledgePathNode(
                key="page",
                label=f"Page {page_number}",
                kind="page",
            )
        )
    if section:
        short = section if len(section) <= 40 else section[:37] + "…"
        nodes.append(KnowledgePathNode(key="section", label=short, kind="section"))
    if chunk_index is not None:
        nodes.append(
            KnowledgePathNode(
                key="chunk",
                label="Matching excerpt (this result)",
                kind="chunk",
                active=True,
            )
        )

    if nodes and nodes[-1].kind != "chunk":
        nodes[-1] = nodes[-1].model_copy(update={"active": True})

    return nodes
