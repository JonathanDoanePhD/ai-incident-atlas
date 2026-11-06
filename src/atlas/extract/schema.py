"""Pydantic schema for one LLM-extracted incident record, plus taxonomy-aware validation.

A record is *structurally* valid if it parses into :class:`IncidentRecord` (all term IDs exist in the taxonomy,
confirmed tags carry a quote and report number, quotes are short). Quote *grounding* (verbatim presence in the
cached report text) is checked separately in :mod:`atlas.extract.grounding` because it needs the database.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from atlas import taxonomy

MAX_QUOTE_WORDS = 25


class Tag(BaseModel):
    id: str
    evidence: Literal["confirmed", "inferred"]
    quote: Optional[str] = None
    report: Optional[int] = None

    @model_validator(mode="after")
    def _evidence_rules(self) -> "Tag":
        if self.evidence == "confirmed":
            if not self.quote or self.report is None:
                raise ValueError(f"confirmed tag '{self.id}' needs a quote and a report number")
        if self.quote is not None:
            q = self.quote.strip()
            if not q:
                self.quote = None
            elif len(q.split()) > MAX_QUOTE_WORDS:
                raise ValueError(f"quote for '{self.id}' exceeds {MAX_QUOTE_WORDS} words")
        return self


def _check_terms(dimension: str, tags: list[Tag]) -> list[Tag]:
    allowed = set(taxonomy.term_ids(dimension))
    seen: set[str] = set()
    out = []
    for t in tags:
        if t.id not in allowed:
            raise ValueError(f"unknown {dimension} term '{t.id}'")
        if t.id not in seen:  # drop exact duplicates silently
            seen.add(t.id)
            out.append(t)
    return out


class Tags(BaseModel):
    sector: list[Tag] = Field(default_factory=list)
    technology: list[Tag] = Field(default_factory=list)
    failure_mode: list[Tag] = Field(default_factory=list)
    harm_type: list[Tag] = Field(default_factory=list)
    lifecycle_stage: list[Tag] = Field(default_factory=list)
    affected_population: list[Tag] = Field(default_factory=list)

    @model_validator(mode="after")
    def _terms(self) -> "Tags":
        for dim in taxonomy.TAG_DIMENSIONS:
            setattr(self, dim, _check_terms(dim, getattr(self, dim)))
        return self


class IncidentRecord(BaseModel):
    incident_id: int
    summary: str = Field(min_length=20, max_length=600)
    technical_summary: str = Field(min_length=20, max_length=800)
    systems: list[str] = Field(default_factory=list)
    developers: list[str] = Field(default_factory=list)
    deployers: list[str] = Field(default_factory=list)
    tags: Tags
    primary_failure_mode: Optional[str] = None
    severity: Optional[Tag] = None
    risk_domain: Optional[str] = None
    risk_subdomain: Optional[str] = None
    intent: Optional[Literal["intentional", "unintentional", "other"]] = None
    cause_entity: Optional[Literal["ai", "human", "other"]] = None
    notes: Optional[str] = None

    @field_validator("intent", "cause_entity", mode="before")
    @classmethod
    def _legacy_unclear(cls, v):  # prompt v1 used 'unclear'; v1.1 aligns with MIT's 'Other'
        return "other" if v == "unclear" else v

    @field_validator("risk_domain", "risk_subdomain", mode="before")
    @classmethod
    def _str_id(cls, v):
        return None if v is None else str(v).strip()

    @model_validator(mode="after")
    def _risk_ids(self) -> "IncidentRecord":
        if self.risk_domain is not None and self.risk_domain not in taxonomy.term_ids("risk_domain"):
            raise ValueError(f"unknown risk_domain '{self.risk_domain}'")
        if self.risk_subdomain is not None:
            if self.risk_subdomain not in taxonomy.term_ids("risk_subdomain"):
                raise ValueError(f"unknown risk_subdomain '{self.risk_subdomain}'")
            if self.risk_domain is None:
                self.risk_domain = self.risk_subdomain.split(".")[0]
            elif not self.risk_subdomain.startswith(self.risk_domain + "."):
                raise ValueError("risk_subdomain does not belong to risk_domain")
        return self

    @field_validator("primary_failure_mode")
    @classmethod
    def _pfm(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in taxonomy.term_ids("failure_mode"):
            raise ValueError(f"unknown primary_failure_mode '{v}'")
        return v

    @field_validator("severity")
    @classmethod
    def _sev(cls, v: Optional[Tag]) -> Optional[Tag]:
        if v is not None and v.id not in taxonomy.term_ids("severity"):
            raise ValueError(f"unknown severity '{v.id}'")
        return v

    @model_validator(mode="after")
    def _primary_in_tags(self) -> "IncidentRecord":
        ids = {t.id for t in self.tags.failure_mode}
        if self.primary_failure_mode and self.primary_failure_mode not in ids:
            # The primary failure mode must also appear among the failure_mode tags (as inferred at least).
            self.tags.failure_mode.append(Tag(id=self.primary_failure_mode, evidence="inferred"))
        return self

    def all_tags(self) -> list[tuple[str, Tag]]:
        out = [(dim, t) for dim in taxonomy.TAG_DIMENSIONS for t in getattr(self.tags, dim)]
        if self.severity is not None:
            out.append(("severity", self.severity))
        return out
