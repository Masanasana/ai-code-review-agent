"""GitHub API service for public pull-request reviews."""

from urllib.parse import urlparse

import httpx

from app.config import settings


GITHUB_API_URL = "https://api.github.com"
GITHUB_API_VERSION = "2022-11-28"


class GitHubReviewPermissionError(Exception):
    """Raised when the configured GitHub identity cannot post a review."""


def get_github_headers(accept: str = "application/vnd.github+json") -> dict[str, str]:
    """Build GitHub API headers, using authentication when configured."""

    headers = {
        "Accept": accept,
        "X-GitHub-Api-Version": GITHUB_API_VERSION,
    }

    # Public repositories can be read without authentication.
    # If a token is configured, use it for higher API limits and
    # for the optional operation of posting a review.
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"

    return headers


def parse_pull_request_url(pr_url: str) -> tuple[str, str, int]:
    """
    Extract owner, repository and pull-request number from a GitHub URL.

    Accepted format:
        https://github.com/<owner>/<repository>/pull/<number>
    """

    parsed_url = urlparse(pr_url.strip())

    if parsed_url.scheme != "https" or parsed_url.netloc.lower() not in {
        "github.com",
        "www.github.com",
    }:
        raise ValueError("URL must be an HTTPS GitHub pull request URL")

    path_parts = [part for part in parsed_url.path.strip("/").split("/") if part]

    if len(path_parts) != 4 or path_parts[2].lower() != "pull":
        raise ValueError(
            "Invalid GitHub pull request URL. Expected "
            "https://github.com/owner/repository/pull/123"
        )

    owner, repo, _, pull_number_text = path_parts

    if not owner or not repo:
        raise ValueError("GitHub owner and repository are required")

    try:
        pull_number = int(pull_number_text)
    except ValueError as exc:
        raise ValueError("Pull request number must be an integer") from exc

    if pull_number <= 0:
        raise ValueError("Pull request number must be greater than zero")

    return owner, repo, pull_number


async def get_pull_request(owner: str, repo: str, pull_number: int) -> dict:
    """Retrieve pull-request metadata from GitHub."""

    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/pulls/{pull_number}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, headers=get_github_headers())

    response.raise_for_status()
    return response.json()


async def get_pull_request_diff(owner: str, repo: str, pull_number: int) -> str:
    """Retrieve the unified diff for a GitHub pull request."""

    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/pulls/{pull_number}"

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(
            url,
            headers=get_github_headers("application/vnd.github.diff"),
        )

    response.raise_for_status()
    return response.text


async def post_pull_request_review(
    owner: str,
    repo: str,
    pull_number: int,
    review_body: str,
) -> dict | None:
    """
    Try to post the AI review to GitHub.

    Reading a public repository only requires read access. Posting a
    review requires write permission on the repository, so failure to
    post is deliberately non-fatal to the AI review itself.
    """

    if not settings.github_token:
        return None

    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/pulls/{pull_number}/reviews"

    headers = get_github_headers()
    headers["Content-Type"] = "application/json"

    payload = {
        "body": review_body,
        "event": "COMMENT",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, headers=headers, json=payload)

    # These statuses mean the configured identity cannot post a review
    # to this repository/PR. The AI review should still be returned.
    if response.status_code in {401, 403, 404, 422}:
        return None

    response.raise_for_status()
    return response.json()
