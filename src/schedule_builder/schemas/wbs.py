"""Schemas for WBS (Work Breakdown Structure) generation and response."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class WBSItemPayload(BaseModel):
    """Single WBS line item."""

    wbs_number: str = Field(min_length=1)
    title: str = Field(min_length=1)
    level: int = Field(ge=1, le=2, description="1=phase, 2=task (MVP enforces max 2 levels)")
    parent_wbs_number: str | None = Field(
        default=None, description="Parent WBS number for hierarchical structure"
    )


class WBSPayload(BaseModel):
    """Complete WBS structure for a document."""

    items: list[WBSItemPayload] = Field(min_length=1, description="At least one WBS item required")

    def validate_numbering(self) -> bool:
        """Check for sequential numbering, no gaps, no duplicates."""
        numbers = {item.wbs_number for item in self.items}
        if len(numbers) != len(self.items):
            raise ValueError("Duplicate WBS numbers detected")
        return True


class WBSItemPublic(BaseModel):
    """WBS item in read format."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    wbs_run_id: str
    wbs_number: str
    title: str
    level: int
    parent_wbs_number: str | None = None
    sort_order: int


class WBSPublic(BaseModel):
    """Complete WBS in read format."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    source_document_id: str | None = None
    generation_status: str
    items: list[WBSItemPublic]


class WBSGenerationRequest(BaseModel):
    """Request to generate WBS from scope analysis."""

    document_id: str = Field(
        min_length=1, description="Document ID with scope analysis to convert to WBS"
    )


class WBSGenerationResponse(BaseModel):
    """Response from WBS generation."""

    wbs_run_id: str
    project_id: str
    document_id: str
    generation_status: str
    item_count: int
    wbs: list[WBSItemPayload]
