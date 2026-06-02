from typing import Any

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str
    message: str


class GitHubRateLimit(BaseModel):
    remaining: int | None = None
    reset_epoch: int | None = None


class ToolResponse(BaseModel):
    ok: bool
    data: Any = None
    error: ErrorDetail | None = None
    rate_limit: GitHubRateLimit | None = None
    warnings: list[str] = Field(default_factory=list)
