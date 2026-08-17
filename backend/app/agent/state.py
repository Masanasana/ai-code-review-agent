"""
State definition for the AI code review agent.

LangGraph passes this state between the different nodes
in our review workflow.
"""

from typing import TypedDict

from app.models import CodeReview


class ReviewState(TypedDict, total=False):
    """
    Shared state used by the code review agent.

    Each node in the LangGraph workflow can read values from
    this state and add/update values for the next node.
    """

    # ---------------------------------------------------------
    # GitHub information
    # ---------------------------------------------------------

    # Original GitHub pull request URL supplied by the user.
    pr_url: str

    # Repository owner.
    owner: str

    # Repository name.
    repo: str

    # Pull request number.
    pull_number: int

    # ---------------------------------------------------------
    # Diff information
    # ---------------------------------------------------------

    # Original diff retrieved from GitHub.
    raw_diff: str

    # Cleaned diff that will be sent to the AI model.
    cleaned_diff: str

    # ---------------------------------------------------------
    # AI review
    # ---------------------------------------------------------

    # Structured review returned by the LLM.
    review: CodeReview

    # Markdown representation of the review.
    review_markdown: str

    # ---------------------------------------------------------
    # GitHub result
    # ---------------------------------------------------------

    # URL of the review posted back to GitHub.
    github_review_url: str