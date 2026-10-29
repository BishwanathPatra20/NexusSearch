from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class OnboardingItem(BaseModel):
    id: int
    sheet_name: str
    row_index: int
    day_label: Optional[str] = None
    category: str = "general"
    title: str
    description: Optional[str] = None
    owner: Optional[str] = None
    confluence_url: Optional[str] = None
    ticket_url: Optional[str] = None
    access_group: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    source_file: Optional[str] = None
    updated_at: datetime


class OnboardingImportResult(BaseModel):
    source_file: str
    sheets_processed: int
    rows_imported: int
    search_document_id: Optional[int] = None
    message: str


class OnboardingListResponse(BaseModel):
    total: int
    items: List[OnboardingItem]
    categories: List[str] = Field(default_factory=list)
    days: List[str] = Field(default_factory=list)
    source_file: Optional[str] = None
    last_import_at: Optional[datetime] = None


class OnboardingMeta(BaseModel):
    total: int
    source_file: Optional[str] = None
    last_import_at: Optional[datetime] = None
    categories: List[str] = Field(default_factory=list)
    days: List[str] = Field(default_factory=list)


class SuggestedAskItem(BaseModel):
    question: str
    source_title: Optional[str] = None
    category: Optional[str] = None


class SuggestedAsksResponse(BaseModel):
    items: List[SuggestedAskItem] = Field(default_factory=list)


class OnboardingLinkHealthItem(BaseModel):
    onboarding_id: int
    title: str
    confluence_url: Optional[str] = None
    page_id: Optional[str] = None
    issue: Optional[str] = None


class OnboardingLinkHealthResponse(BaseModel):
    total_with_url: int
    parseable: int
    items: List[OnboardingLinkHealthItem] = Field(default_factory=list)


class OnboardingConfluenceSyncResult(BaseModel):
    requested: int
    indexed: int
    errors: List[str] = Field(default_factory=list)
    message: str
