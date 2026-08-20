"""State definition for the LangGraph code-review workflow."""

from typing import TypedDict

from app.models import CodeReview


class ReviewState(TypedDict, total=False):
    pr_url: str

    owner: str
    repo: str
    pull_number: int

    # Metadata returned by GitHub.
    is_public: bool
    pull_request_url: str

    raw_diff: str
    cleaned_diff: str

    review: CodeReview
    review_markdown: str

    github_review_url: str | None
    github_review_posted: bool
    github_message: str
