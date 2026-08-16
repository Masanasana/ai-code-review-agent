"""
GitHub API service.

This module contains functions responsible for communicating
with the GitHub REST API.

Keeping GitHub-related logic here means that our FastAPI routes
do not need to know how the GitHub API works.
"""

import httpx


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