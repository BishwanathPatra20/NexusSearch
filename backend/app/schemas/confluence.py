from typing import List, Optional

from pydantic import BaseModel, Field


class ConfluenceStatus(BaseModel):
    enabled: bool
    configured: bool
    base_url: Optional[str] = None
    reachable: bool = False
    user_display_name: Optional[str] = None
    message: str


class ConfluenceSpaceOut(BaseModel):
    key: str
    name: str
    type: Optional[str] = None


class ConfluenceSyncRequest(BaseModel):
    space_key: str = Field(..., min_length=1, max_length=64)
    limit: int = Field(25, ge=1, le=100)
    tags: List[str] = Field(default_factory=list)
    replace_existing: bool = True


class ConfluenceSyncResult(BaseModel):
    space_key: str
    pages_fetched: int
    pages_indexed: int
    skipped: int
    errors: List[str] = Field(default_factory=list)


class ConfluenceSpaceValidate(BaseModel):
    key: str
    name: str
    type: Optional[str] = None
    found: bool = True


class ConfluencePageSyncRequest(BaseModel):
    page_id: str = Field(..., min_length=1, max_length=32)
    tags: List[str] = Field(default_factory=list)
    replace_existing: bool = True


class ConfluencePageSyncResult(BaseModel):
    page_id: str
    title: str
    space_key: Optional[str] = None
    indexed: bool
    message: str


class ConfluencePagesSyncRequest(BaseModel):
    page_ids: List[str] = Field(..., min_length=1, max_length=200)
    tags: List[str] = Field(default_factory=list)
    replace_existing: bool = True


class ConfluencePagesSyncResult(BaseModel):
    requested: int
    indexed: int
    skipped: int
    results: List[ConfluencePageSyncResult] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)


class ConfluenceDescendantsSyncRequest(BaseModel):
    parent_page_id: str = Field(..., min_length=1, max_length=32)
    max_pages: int = Field(50, ge=1, le=200)
    include_parent: bool = True
    tags: List[str] = Field(default_factory=list)
    replace_existing: bool = True


class ConfluenceSyncJobRequest(BaseModel):
    space_key: Optional[str] = Field(None, max_length=64)
    limit: int = Field(100, ge=1, le=200)
    parent_page_id: Optional[str] = Field(None, max_length=32)
    max_pages: int = Field(100, ge=1, le=200)
    tags: List[str] = Field(default_factory=list)
    replace_existing: bool = True


class ConfluenceSyncJobResponse(BaseModel):
    job_id: int
    message: str
