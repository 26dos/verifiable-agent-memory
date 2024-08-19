"""Typed schema for agent decision traces.

We don't enforce these types on-chain — the chain only stores the hash.
This module is for off-chain producers and consumers so they agree on what
the bytes were before they got hashed.
"""
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class InputSnapshot(BaseModel):
    """Whatever the agent saw when making the decision."""
    prices: dict[str, float] = Field(default_factory=dict)
    position: dict[str, Any] = Field(default_factory=dict)
    extra: dict[str, Any] = Field(default_factory=dict)


class ReasoningStep(BaseModel):
    """One step in the agent's chain of thought."""
    role: str
    content: str
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)


class Decision(BaseModel):
    """The action the agent decided to take."""
    kind: str
    params: dict[str, Any] = Field(default_factory=dict)


class Trace(BaseModel):
    agent_id: str
    model_id: str
    model_version: int = 1
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    input: InputSnapshot
    steps: list[ReasoningStep]
    decision: Decision

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")
