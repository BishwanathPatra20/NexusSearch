from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from backend.app.constants import DocumentStatus


class RelatedDocumentBrief(BaseModel):
    id: int
    title: str
    file_name: str
    status: DocumentStatus


class KnowledgePathNode(BaseModel):
    key: str
    label: str
    kind: str  # root | repository | source | folder | ellipsis | file | page | section | chunk
    active: bool = False


class DocumentSummary(BaseModel):
    id: int
    title: str
    file_name: str
    file_type: str
    tags: List[str] = Field(default_factory=list)
    source_type: str
    source_uri: Optional[str] = None
    source_link: Optional[str] = None
    upload_date: datetime
    view_count: int
    chunk_count: Optional[int] = None
    status: DocumentStatus = DocumentStatus.ACTIVE
    version_label: Optional[str] = None
    related_document_ids: List[int] = Field(default_factory=list)
    related_documents: List[RelatedDocumentBrief] = Field(default_factory=list)
    duplicate_of_ids: List[int] = Field(default_factory=list)
    knowledge_path: List[KnowledgePathNode] = Field(default_factory=list)


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[DocumentStatus] = None
    version_label: Optional[str] = None
    related_document_ids: Optional[List[int]] = None


class ChunkOut(BaseModel):
    id: int
    document_id: int
    page_number: int
    chunk_index: int
    section: Optional[str] = None
    content: str


class SearchHit(BaseModel):
    chunk_id: int
    document_id: int
    document_title: str
    file_name: str
    page_number: int
    chunk_index: int
    snippet: str
    score: float
    document_status: DocumentStatus
    ranking_reasons: List[str] = Field(default_factory=list)
    related_documents: List[RelatedDocumentBrief] = Field(default_factory=list)
    knowledge_path: List[KnowledgePathNode] = Field(default_factory=list)
    source_link: Optional[str] = None
    source_type: Optional[str] = None
    confluence_page_id: Optional[str] = None


class SearchResponse(BaseModel):
    search_id: Optional[int] = None
    query: str
    expanded_terms: List[str] = Field(default_factory=list)
    synonym_groups: List[str] = Field(default_factory=list)
    results_count: int
    results: List[SearchHit]
    filters_applied: dict = Field(default_factory=dict)


class SearchClickRequest(BaseModel):
    search_id: Optional[int] = None
    query: str
    chunk_id: int
    click_position: int = Field(ge=1)


class UploadResponse(BaseModel):
    document: DocumentSummary
    chunks_created: int
    job_id: Optional[int] = None


class FolderIngestRequest(BaseModel):
    folder_path: str
    tags: List[str] = Field(default_factory=list)
    recursive: bool = True
    async_job: bool = True


class FolderIngestResponse(BaseModel):
    job_id: int
    message: str


class JobStatus(BaseModel):
    id: int
    job_type: str
    status: str
    result_json: Optional[dict] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class TopSearchItem(BaseModel):
    query: str
    count: int


class TopDocumentItem(BaseModel):
    document_id: int
    title: str
    file_name: str
    view_count: int


class SearchQualityItem(BaseModel):
    query: str
    searches: int
    success_rate_pct: float
    avg_click_position: Optional[float] = None


class DuplicatePair(BaseModel):
    document_id_a: int
    title_a: str
    document_id_b: int
    title_b: str
    similarity_pct: float
    reason: str


class KnowledgeHealthReport(BaseModel):
    outdated_documents: List[DocumentSummary]
    documents_without_tags: List[DocumentSummary]
    documents_never_accessed: List[DocumentSummary]
    documents_missing_version: List[DocumentSummary]
    potential_duplicates: List[DuplicatePair]


class ConfluenceCorpusStats(BaseModel):
    pages_indexed: int
    last_synced_at: Optional[str] = None


class SearchVolumeDay(BaseModel):
    day: str
    searches: int
    zero_results: int


class AnalyticsSummary(BaseModel):
    top_searches: List[TopSearchItem]
    top_documents: List[TopDocumentItem]
    zero_result_searches: List[TopSearchItem]
    total_searches: int
    search_quality: List[SearchQualityItem]
    search_volume_by_day: List[SearchVolumeDay] = Field(default_factory=list)
    knowledge_health: KnowledgeHealthReport
    confluence: Optional[ConfluenceCorpusStats] = None


class PlanStepOut(BaseModel):
    name: str
    detail: str


class StructuredPlanOut(BaseModel):
    intent: str
    action: str
    requires_sources: bool = True
    requires_review: bool = True
    confidence_threshold: float = 80.0
    routing_notes: List[str] = Field(default_factory=list)


class ExecutionPlanOut(BaseModel):
    query: str
    structured: StructuredPlanOut
    steps: List[PlanStepOut] = Field(default_factory=list)


class ReviewSourceOut(BaseModel):
    chunk_id: int
    document_id: int
    relevance_score: float
    snippet: Optional[str] = None
    file_name: Optional[str] = None
    page_number: Optional[int] = None


class ReviewActionOut(BaseModel):
    id: int
    action: str
    reviewer: str
    comment: Optional[str] = None
    timestamp: datetime


class ReviewItemOut(BaseModel):
    id: int
    query: str
    draft_answer: str
    final_answer: Optional[str] = None
    status: str
    confidence_score: float
    validator_notes: List[str] = Field(default_factory=list)
    plan: Optional[ExecutionPlanOut] = None
    sources: List[ReviewSourceOut] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class AskRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    submit_for_review: bool = True


class AskResponse(BaseModel):
    review_item_id: int
    status: str
    confidence_score: float
    draft_answer: str
    plan: ExecutionPlanOut
    sources: List[ReviewSourceOut]
    validator_notes: List[str]


class ReviewDecisionRequest(BaseModel):
    reviewer: Optional[str] = None
    comment: Optional[str] = None


class ReviewEditRequest(BaseModel):
    final_answer: str = Field(..., min_length=1)
    reviewer: Optional[str] = None
    comment: Optional[str] = None


class ApprovedKnowledgeOut(BaseModel):
    id: int
    review_item_id: int
    query: str
    approved_answer: str
    reviewer: str
    approved_at: datetime


class LineageValidationOut(BaseModel):
    supported: bool
    confidence_score: float
    threshold: float
    notes: List[str] = Field(default_factory=list)


class LineageReviewOut(BaseModel):
    status: str
    final_answer: Optional[str] = None
    last_reviewer: Optional[str] = None
    last_decision_at: Optional[datetime] = None
    decision_label: Optional[str] = None


class LineageSourceOut(ReviewSourceOut):
    document_title: Optional[str] = None
    chunk_index: Optional[int] = None


class LineageStageOut(BaseModel):
    stage: str
    title: str
    detail: Optional[str] = None
    timestamp: Optional[datetime] = None


class KnowledgeLineageOut(BaseModel):
    review_item_id: int
    knowledge_id: Optional[str] = None
    question: str
    plan: Optional[ExecutionPlanOut] = None
    draft_answer: str
    validation: LineageValidationOut
    review: LineageReviewOut
    approved_knowledge: Optional[ApprovedKnowledgeOut] = None
    sources: List[LineageSourceOut] = Field(default_factory=list)
    audit: List[ReviewActionOut] = Field(default_factory=list)
    timeline: List[LineageStageOut] = Field(default_factory=list)


class LineageIndexItem(BaseModel):
    review_item_id: int
    knowledge_id: Optional[str] = None
    question: str
    status: str
    created_at: datetime


class ReviewQualityMetrics(BaseModel):
    questions_asked: int
    pending: int
    approved: int
    rejected: int
    edited: int
    approval_rate_pct: float
    rejection_rate_pct: float
    edit_rate_pct: float


class ValidatorInsightMetrics(BaseModel):
    average_validation_score: float
    low_confidence_drafts: int
    common_validator_notes: List[TopSearchItem]


class TrustedDocumentItem(BaseModel):
    document_id: int
    title: str
    file_name: str
    citation_count: int
    document_status: str


class GovernanceKnowledgeMetrics(BaseModel):
    approved_knowledge_entries: int
    deprecated_source_citations: int
    most_trusted_documents: List[TrustedDocumentItem]


class GovernanceMetricsOut(BaseModel):
    review_quality: ReviewQualityMetrics
    validator_insights: ValidatorInsightMetrics
    knowledge: GovernanceKnowledgeMetrics
    most_reviewed_topics: List[TopSearchItem]
    search_success_queries: List[SearchQualityItem]
    zero_result_searches: List[TopSearchItem]
