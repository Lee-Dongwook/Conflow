"""Documents domain — DocumentTemplate, DocumentInstance, ReviewWorkflow,
RetentionPolicy. Owns formal-document issuance (employment contracts, wage
statements, etc.). Free-form collaboration docs (Notion-style) are
explicitly out of scope through Phase 4 (Anti-Vision).
"""

from .model import (
    DocumentCategory,
    DocumentInstance,
    DocumentInstanceState,
    DocumentTemplate,
    RetentionPolicy,
    ReviewWorkflow,
    ReviewWorkflowState,
    TemplateState,
)

__all__ = [
    "DocumentCategory",
    "DocumentInstance",
    "DocumentInstanceState",
    "DocumentTemplate",
    "RetentionPolicy",
    "ReviewWorkflow",
    "ReviewWorkflowState",
    "TemplateState",
]
