from enum import Enum


class DocumentStatus(str, Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"
    DRAFT = "draft"


STATUS_RANK_BOOST = {
    DocumentStatus.ACTIVE: 12.0,
    DocumentStatus.DRAFT: 4.0,
    DocumentStatus.DEPRECATED: -8.0,
    DocumentStatus.ARCHIVED: -15.0,
}
