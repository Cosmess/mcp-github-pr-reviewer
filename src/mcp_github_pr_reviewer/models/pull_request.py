from pydantic import BaseModel, Field


class PullRequest(BaseModel):
    number: int
    title: str
    state: str
    author: str
    url: str
    body: str = ""
    base_branch: str
    head_branch: str
    changed_files: int = 0
    additions: int = 0
    deletions: int = 0


class ChangedFile(BaseModel):
    filename: str
    status: str
    additions: int = 0
    deletions: int = 0
    changes: int = 0
    patch: str = ""


class PullRequestAnalysis(BaseModel):
    summary: str
    important_files: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    suggested_tests: list[str] = Field(default_factory=list)
    markdown_review: str
