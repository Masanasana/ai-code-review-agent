"""
GitHub API service.

This module contains functions responsible for communicating
with the GitHub REST API.

Keeping GitHub-related logic here means that our FastAPI routes
do not need to know how the GitHub API works.
"""

import httpx
from urllib.parse import urlparse
# Base URL for GitHub's REST API.
# We will append specific endpoints to this URL.
GITHUB_API_URL = "https://api.github.com"

from app.config import settings

async def get_pull_request(
    owner: str,
    repo: str,
    pull_number: int,
):
    """
    Retrieve information about a GitHub pull request.

    Parameters
    ----------
    owner : str
        GitHub username or organisation that owns the repository.

    repo : str
        Name of the GitHub repository.

    pull_number : int
        Number of the pull request.

    Returns
    -------
    dict
        JSON response returned by the GitHub API.

    Raises
    ------
    httpx.HTTPStatusError
        If GitHub returns an unsuccessful HTTP status code.
    """

    # Construct the GitHub API endpoint for the specific PR.
    #
    # Example:
    # https://api.github.com/repos/openai/example/pulls/12
    url = (
        f"{GITHUB_API_URL}/repos/"
        f"{owner}/{repo}/pulls/{pull_number}"
    )

    # Create an asynchronous HTTP client.
    #
    # "async with" ensures that the HTTP connection is properly
    # closed after the request has completed.
    # async with httpx.AsyncClient() as client:

    #     # Send a GET request to GitHub.
    #     response = await client.get(url)

    headers = get_github_headers()

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers=headers,
        )
    # Raise an exception if GitHub returned an error.
    #
    # For example:
    # 404 -> repository or PR does not exist
    # 401 -> authentication problem
    # 403 -> permission/rate-limit problem
    response.raise_for_status()

    # Convert GitHub's JSON response into a Python dictionary
    # and return it to the caller.
    return response.json()


async def get_pull_request_diff(
    owner: str,
    repo: str,
    pull_number: int,
):
    """
    Retrieve the code changes introduced by a pull request.

    GitHub provides the PR diff when we request the pull request
    using the media type:

        application/vnd.github.diff

    The diff is particularly important for our application because
    this is the code that will eventually be sent to the AI model
    for review.

    Parameters
    ----------
    owner : str
        GitHub username or organisation that owns the repository.

    repo : str
        Name of the repository.

    pull_number : int
        Pull request number.

    Returns
    -------
    str
        Unified diff containing the changes made by the PR.
    """

    # Construct the GitHub API endpoint for the pull request.
    url = (
        f"{GITHUB_API_URL}/repos/"
        f"{owner}/{repo}/pulls/{pull_number}"
    )

    # Get our standard authenticated GitHub headers.
    headers = get_github_headers()

    # Override the Accept header because we want the PR
    # returned as a unified diff rather than JSON.
    headers["Accept"] = "application/vnd.github.diff"

    # Create an asynchronous HTTP client.
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers=headers,
        )
    # Raise an exception if GitHub returned an unsuccessful
    # HTTP status code.
    response.raise_for_status()

    # Return the raw diff as text.
    return response.text


def parse_pull_request_url(pr_url: str) -> tuple[str, str, int]:
    """
    Extract the repository owner, repository name, and pull
    request number from a GitHub pull request URL.

    Expected URL format:

        https://github.com/<owner>/<repository>/pull/<number>

    Parameters
    ----------
    pr_url : str
        GitHub pull request URL.

    Returns
    -------
    tuple[str, str, int]
        A tuple containing:

        - repository owner
        - repository name
        - pull request number

    Raises
    ------
    ValueError
        If the supplied URL is not a valid GitHub pull request URL.
    """

    # Parse the URL into its individual components.
    parsed_url = urlparse(pr_url)

    # Make sure the URL actually points to GitHub.
    if parsed_url.netloc.lower() != "github.com":
        raise ValueError("URL must belong to github.com")

    # Remove leading/trailing slashes and split the path.
    #
    # Example:
    #
    # /Masanasana/ai-code-review-agent/pull/2
    #
    # becomes:
    #
    # ["Masanasana", "ai-code-review-agent", "pull", "2"]
    path_parts = parsed_url.path.strip("/").split("/")

    # A valid PR URL should have exactly this structure:
    #
    # owner / repository / pull / number
    if len(path_parts) != 4:
        raise ValueError("Invalid GitHub pull request URL")

    owner = path_parts[0]
    repo = path_parts[1]
    pull_keyword = path_parts[2]
    pull_number = path_parts[3]

    # Make sure this is actually a pull request URL.
    if pull_keyword != "pull":
        raise ValueError("URL does not point to a pull request")

    # Convert the PR number from a string into an integer.
    try:
        pull_number = int(pull_number)
    except ValueError:
        raise ValueError("Pull request number must be an integer")

    return owner, repo, pull_number

def get_github_headers() -> dict[str, str]:
    """
    Build the HTTP headers used when communicating with GitHub.

    The Authorization header allows us to make authenticated
    requests using the GitHub token stored in our environment.
    """

    return {
        "Authorization": f"Bearer {settings.github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


async def post_pull_request_review(
    owner: str,
    repo: str,
    pull_number: int,
    review_body: str,
):
    """
    Post a review to a GitHub pull request.

    Parameters
    ----------
    owner : str
        GitHub username or organisation that owns the repository.

    repo : str
        Name of the repository.

    pull_number : int
        Pull request number.

    review_body : str
        Markdown-formatted review generated by the AI agent.

    Returns
    -------
    dict
        GitHub API response containing information about the
        newly created review.
    """

    # GitHub endpoint used to create a pull request review.
    url = (
        f"{GITHUB_API_URL}/repos/"
        f"{owner}/{repo}/pulls/{pull_number}/reviews"
    )

    # Get our standard authenticated GitHub headers.
    headers = get_github_headers()

    # Tell GitHub that we are sending JSON.
    headers["Content-Type"] = "application/json"

    # Build the request body.
    #
    # "COMMENT" means the review will be posted as a comment
    # rather than approving or rejecting the pull request.
    payload = {
        "body": review_body,
        "event": "COMMENT",
    }

    # Send the review to GitHub.
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            headers=headers,
            json=payload,
        )

    # Raise an exception if GitHub rejects the request.
    response.raise_for_status()

    # Return GitHub's response as a Python dictionary.
    return response.json()