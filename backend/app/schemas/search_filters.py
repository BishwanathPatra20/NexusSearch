from typing import Optional

from pydantic import BaseModel, Field


class SearchFilters(BaseModel):
    status: Optional[str] = Field(None, description="active | deprecated | archived | draft")
    tag: Optional[str] = None
    file_type: Optional[str] = Field(None, description="pdf, docx, txt, md, html without dot")
    version_label: Optional[str] = None
