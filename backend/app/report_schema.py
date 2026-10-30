"""Closed report plans: the LLM selects evidence, never writes numerical claims."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class GemmaPlan(StrictModel):
    observed_signal_evidence: list[str] = Field(min_length=3, max_length=6)
    healthy_reference_comparison: list[str] = Field(min_length=1, max_length=3)
    hypothesis: Literal["descriptive_profile_difference", "physical_cause_not_established"]

    @field_validator("observed_signal_evidence", "healthy_reference_comparison")
    @classmethod
    def unique_references(cls, value):
        if len(value) != len(set(value)):
            raise ValueError("Duplicate evidence reference")
        return value


class ReportSection(StrictModel):
    title: str
    kind: Literal["measurement", "model_prediction", "hypothesis", "limitation", "context"]
    statements: list[str] = Field(min_length=1)
    evidence_ids: list[str] = Field(default_factory=list)


class ForensicReport(StrictModel):
    cycle_id: int
    source: str
    mode: Literal["gemma", "fallback"]
    inference_mode: Literal["live_local", "precomputed", "non_llm"] = "live_local"
    narrative: str
    structured_evidence: list[str]
    sections: list[ReportSection] = Field(min_length=6, max_length=6)
    warning: str
    selected_model: str
    generation: dict
    evidence_sha256: str
    fallback_reason: str | None = None
