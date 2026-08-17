"""
LangGraph workflow for the AI code review agent.

This module orchestrates the individual services that perform
the GitHub pull request review.
"""

from langgraph.graph import StateGraph, START, END

from app.agent.state import ReviewState

from app.services.github import (
    parse_pull_request_url,
    get_pull_request_diff,
    post_pull_request_review,
)

from app.services.diff_processor import clean_diff

from app.services.llm import review_code

from app.services.review_formatter import format_review_as_markdown


def parse_pr_node(state: ReviewState) -> ReviewState:
    """
    Parse the GitHub pull request URL.

    Converts:

        https://github.com/owner/repository/pull/123

    into:

        owner
        repository
        123
    """

    # Extract repository information from the PR URL.
    owner, repo, pull_number = parse_pull_request_url(
        state["pr_url"]
    )

    # Add the parsed information to the shared agent state.
    return {
        "owner": owner,
        "repo": repo,
        "pull_number": pull_number,
    }

async def fetch_diff_node(state: ReviewState) -> ReviewState:
    """
    Retrieve the raw pull request diff from GitHub.
    """

    # Request the diff from GitHub.
    raw_diff = await get_pull_request_diff(
        owner=state["owner"],
        repo=state["repo"],
        pull_number=state["pull_number"],
    )

    # Store the raw diff in the agent state.
    return {
        "raw_diff": raw_diff,
    }

def clean_diff_node(state: ReviewState) -> ReviewState:
    """
    Remove irrelevant files from the GitHub diff.
    """

    # Clean the raw GitHub diff.
    cleaned_diff = clean_diff(
        state["raw_diff"]
    )

    # Store the cleaned version in the state.
    return {
        "cleaned_diff": cleaned_diff,
    }

async def review_code_node(state: ReviewState) -> ReviewState:
    """
    Send the cleaned pull request diff to the AI model.
    """

    # Ask the LLM to analyse the code changes.
    review = await review_code(
        state["cleaned_diff"]
    )

    # Store the structured review in the state.
    return {
        "review": review,
    }

def format_review_node(state: ReviewState) -> ReviewState:
    """
    Convert the structured AI review into Markdown.
    """

    # Convert the Pydantic CodeReview object into
    # Markdown suitable for GitHub.
    review_markdown = format_review_as_markdown(
        state["review"]
    )

    # Store the Markdown version in the state.
    return {
        "review_markdown": review_markdown,
    }

async def post_review_node(state: ReviewState) -> ReviewState:
    """
    Post the AI-generated review back to GitHub.
    """

    # Send the formatted review to GitHub.
    github_review = await post_pull_request_review(
        owner=state["owner"],
        repo=state["repo"],
        pull_number=state["pull_number"],
        review_body=state["review_markdown"],
    )

    # Extract the URL of the newly created GitHub review.
    return {
        "github_review_url": github_review["html_url"],
    }


def build_review_graph():
    """
    Build and compile the AI code review workflow.
    """

    # Create a graph using our ReviewState definition.
    graph = StateGraph(ReviewState)

    # ---------------------------------------------------------
    # Register nodes
    # ---------------------------------------------------------

    graph.add_node(
        "parse_pr",
        parse_pr_node,
    )

    graph.add_node(
        "fetch_diff",
        fetch_diff_node,
    )

    graph.add_node(
        "clean_diff",
        clean_diff_node,
    )

    graph.add_node(
        "review_code",
        review_code_node,
    )

    graph.add_node(
        "format_review",
        format_review_node,
    )

    graph.add_node(
        "post_review",
        post_review_node,
    )

    # ---------------------------------------------------------
    # Define workflow
    # ---------------------------------------------------------

    graph.add_edge(
        START,
        "parse_pr",
    )

    graph.add_edge(
        "parse_pr",
        "fetch_diff",
    )

    graph.add_edge(
        "fetch_diff",
        "clean_diff",
    )

    graph.add_edge(
        "clean_diff",
        "review_code",
    )

    graph.add_edge(
        "review_code",
        "format_review",
    )

    graph.add_edge(
        "format_review",
        "post_review",
    )

    graph.add_edge(
        "post_review",
        END,
    )

    # Compile the graph so that it can be executed.
    return graph.compile()


# Create one compiled instance of the review agent.
review_graph = build_review_graph()