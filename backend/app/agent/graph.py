"""LangGraph workflow for the AI code review agent."""

from langgraph.graph import END, START, StateGraph

from app.agent.state import ReviewState
from app.services.diff_processor import clean_diff
from app.services.github import (
    get_pull_request,
    get_pull_request_diff,
    parse_pull_request_url,
    post_pull_request_review,
)
from app.services.llm import review_code
from app.services.review_formatter import format_review_as_markdown


def parse_pr_node(state: ReviewState) -> ReviewState:
    """Parse any valid GitHub pull-request URL."""

    owner, repo, pull_number = parse_pull_request_url(state["pr_url"])

    return {
        "owner": owner,
        "repo": repo,
        "pull_number": pull_number,
    }


async def validate_pr_node(state: ReviewState) -> ReviewState:
    """Verify that the PR exists and belongs to a public repository."""

    pull_request = await get_pull_request(
        owner=state["owner"],
        repo=state["repo"],
        pull_number=state["pull_number"],
    )

    repository = pull_request.get("base", {}).get("repo", {})

    if repository.get("private", True):
        raise ValueError(
            "This application currently reviews public GitHub repositories only."
        )

    return {
        "is_public": True,
        "pull_request_url": pull_request.get("html_url", state["pr_url"]),
    }


async def fetch_diff_node(state: ReviewState) -> ReviewState:
    """Retrieve the raw pull-request diff from GitHub."""

    raw_diff = await get_pull_request_diff(
        owner=state["owner"],
        repo=state["repo"],
        pull_number=state["pull_number"],
    )

    if not raw_diff.strip():
        raise ValueError("No changes were found in this pull request.")

    return {"raw_diff": raw_diff}


def clean_diff_node(state: ReviewState) -> ReviewState:
    """Remove files that are not relevant for AI code review."""

    cleaned = clean_diff(state["raw_diff"])

    if not cleaned.strip():
        raise ValueError("No reviewable source-code changes found in the pull request.")

    return {"cleaned_diff": cleaned}


async def review_code_node(state: ReviewState) -> ReviewState:
    """Send the cleaned diff to the AI reviewer."""

    review = await review_code(state["cleaned_diff"])
    return {"review": review}


def format_review_node(state: ReviewState) -> ReviewState:
    """Convert the structured review into Markdown."""

    return {
        "review_markdown": format_review_as_markdown(state["review"]),
    }


async def post_review_node(state: ReviewState) -> ReviewState:
    """
    Try to post the review to GitHub.

    This is best-effort. A user can review any public repository even
    when the application's GitHub account does not have write access.
    """

    github_review = await post_pull_request_review(
        owner=state["owner"],
        repo=state["repo"],
        pull_number=state["pull_number"],
        review_body=state["review_markdown"],
    )

    if github_review:
        return {
            "github_review_url": github_review.get("html_url"),
            "github_review_posted": True,
            "github_message": "The AI review was posted directly to GitHub.",
        }

    return {
        "github_review_url": None,
        "github_review_posted": False,
        "github_message": (
            "The pull request was reviewed successfully, but the configured "
            "GitHub account does not have permission to post a review on this repository."
        ),
    }


def build_review_graph():
    graph = StateGraph(ReviewState)

    graph.add_node("parse_pr", parse_pr_node)
    graph.add_node("validate_pr", validate_pr_node)
    graph.add_node("fetch_diff", fetch_diff_node)
    graph.add_node("clean_diff", clean_diff_node)
    graph.add_node("review_code", review_code_node)
    graph.add_node("format_review", format_review_node)
    graph.add_node("post_review", post_review_node)

    graph.add_edge(START, "parse_pr")
    graph.add_edge("parse_pr", "validate_pr")
    graph.add_edge("validate_pr", "fetch_diff")
    graph.add_edge("fetch_diff", "clean_diff")
    graph.add_edge("clean_diff", "review_code")
    graph.add_edge("review_code", "format_review")
    graph.add_edge("format_review", "post_review")
    graph.add_edge("post_review", END)

    return graph.compile()


review_graph = build_review_graph()
