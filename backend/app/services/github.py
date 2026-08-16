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
    async with httpx.AsyncClient() as client:

        # Send a GET request to GitHub.
        response = await client.get(url)

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

    # Tell GitHub that we specifically want the PR represented
    # as a unified diff rather than the normal JSON response.
    headers = {
        "Accept": "application/vnd.github.diff"
    }

    # Create an asynchronous HTTP client.
    async with httpx.AsyncClient() as client:

        # Request the PR diff.
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