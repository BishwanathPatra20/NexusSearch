from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KNOWLEDGEPILOT_",
        env_file=".env",
        extra="ignore",
    )

    host: str = "127.0.0.1"
    port: int = 8000
    data_dir: Path = Path("./data")
    offline_mode: bool = True
    max_chars_per_chunk: int = 4000
    chunk_overlap_chars: int = 200
    api_prefix: str = "/api/v1"
    folder_ingest_max_files: int = 500
    folder_ingest_max_file_mb: int = 25
    review_auto_approve_min_confidence: float = 101.0
    default_reviewer: str = "local-reviewer"
    synonyms_path: Path = Path("./config/synonyms.json")
    planner_confidence_threshold: float = 80.0
    onboarding_dir: Path = Path("./config/onboarding")
    onboarding_xlsx_filename: str = "Personalization_KT_Onboarding_10Day.xlsx"

    # Confluence Cloud (optional — outbound HTTPS to your Atlassian site only)
    confluence_enabled: bool = False
    confluence_base_url: Optional[str] = None
    confluence_email: Optional[str] = None
    confluence_api_token: Optional[str] = None
    confluence_verify_ssl: bool = True
    # basic = email+token (Cloud). bearer = PAT header (most Server/Data Center).
    # auto = bearer for non-atlassian.net hosts, else basic.
    confluence_auth_mode: str = "auto"
    # When false, status/spaces work but sync endpoints return 403 (read-only / audit mode).
    confluence_sync_enabled: bool = True
    # Fetch Confluence pages over PAT during Search when not in the local index (page id / title).
    confluence_live_search_enabled: bool = True
    hybrid_rerank_enabled: bool = True

    # Local RAG bot (optional Ollama on localhost — no cloud SDKs)
    rag_bot_enabled: bool = True
    rag_llm_enabled: bool = True
    rag_top_k: int = 8
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "llama3.2"
    ollama_timeout_sec: float = 90.0
    ollama_temperature: float = 0.2

    # Scheduled Confluence refresh (optional; uses PAT only).
    confluence_scheduled_space_key: Optional[str] = None
    confluence_scheduled_parent_page_id: Optional[str] = None
    confluence_scheduled_max_pages: int = 50
    confluence_schedule_cron_hour: int = 6
    confluence_schedule_cron_minute: int = 0

    # Optional Bearer token for /orchestrate and /automations (unset = localhost trust)
    api_key: Optional[str] = None
    agent_reports_dir: Path = Path("./data/agent_reports")
    automation_suggested_ask_limit: int = 5
    automation_reject_below_score: float = 35.0

    # Ingest watcher — poll folder on schedule / ingest_watcher agent
    watch_enabled: bool = False
    watch_folder: Optional[Path] = None
    watch_folders: Optional[str] = None  # comma-separated; overrides single watch_folder when set
    watch_recursive: bool = True
    watch_tags: str = "watched,auto-ingest"
    notify_webhook_url: Optional[str] = None

    @property
    def db_path(self) -> Path:
        return self.data_dir / "knowledgepilot.db"

    @property
    def uploads_dir(self) -> Path:
        return self.data_dir / "uploads"


settings = Settings()
