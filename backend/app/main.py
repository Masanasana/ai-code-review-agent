
"""
Main entry point for the AI Code Review Agent API.

This module creates the FastAPI application and defines
the initial API endpoints.
"""
from fastapi import FastAPI

# Import the Pydantic model used to validate incoming
# pull request requests.
from app.models import ReviewRequest

# Import our GitHub service function.
#
# The actual GitHub API communication is kept inside
# services/github.py rather than inside this file.
from app.services.github import (
    get_pull_request,
    get_pull_request_diff
)
#Import diff processor
from app.services.diff_processor import clean_diff


# Create an instance of the FastAPI application.
#
# This 'app' object is the main entry point for our backend.
# We will attach our API endpoints (routes) to this object below.
app = FastAPI(
    # The name displayed in the automatically generated API documentation.
    title="AI Code Review Agent",

    # A short description of what our API is responsible for.
    description="Backend API for an AI-powered GitHub code review agent.",

    # Version number for our API.
    # This is useful when we eventually make changes to the API.
    version="0.1.0",
)


# Define a GET endpoint at the root URL: "/"
#
# When someone sends a GET request to:
#     http://127.0.0.1:8000/
#
# FastAPI will execute this function.
@app.get("/")
async def root():

    # Return a Python dictionary.
    # FastAPI automatically converts this dictionary into JSON.
    return {
        "message": "AI Code Review Agent API is running"
    }


# Define another GET endpoint at "/health".
#
# This endpoint is commonly called a "health check".
# It allows us, or a deployment platform, to quickly check
# whether our backend is running correctly.
#
# URL:
#     http://127.0.0.1:8000/health
@app.get("/health")
async def health_check():

    # Return a simple JSON response indicating that
    # the application is healthy and running.
    return {
        "status": "healthy"
    }


# Define a POST endpoint at /review.
# The frontend will use this endpoint when it wants the AI agent
# to review a GitHub Pull Request.
@app.post("/review")
async def review_pull_request(request: ReviewRequest):

    # Return a JSON response confirming that the Pull Request
    # was successfully received by the backend.
    return {
        "message": "Pull request received",

        # Convert the Pydantic HttpUrl object to a regular string
        # so it can be returned cleanly as JSON.
        "pr_url": str(request.pr_url),
    }

# -------------------------------------------------------------------
# GitHub Integration Test Endpoint
# -------------------------------------------------------------------

@app.get("/github-test/{owner}/{repo}/{pull_number}")
async def github_test(
    owner: str,
    repo: str,
    pull_number: int,
):
    """
    Test our connection to the GitHub API.

    This endpoint is temporary.

    It allows us to verify that our GitHub service works before
    connecting it to the AI agent.

    Example:

        GET /github-test/openai/example/1

    The endpoint retrieves the PR from GitHub and returns a
    small subset of the information.
    """

    # Call the GitHub service.
    #
    # Notice that main.py does NOT contain the HTTP request
    # itself. That responsibility belongs to github.py.
    pull_request = await get_pull_request(
        owner,
        repo,
        pull_number,
    )

    # Return only the information we currently need.
    #
    # The GitHub API returns a large JSON object containing
    # many fields. We don't need to expose all of them.
    return {
        "title": pull_request["title"],
        "state": pull_request["state"],
        "user": pull_request["user"]["login"],
        "url": pull_request["html_url"],
    }


@app.get("/github-test/{owner}/{repo}/{pull_number}/diff")
async def github_diff_test(
    owner: str,
    repo: str,
    pull_number: int,
):
    """
    Test endpoint for retrieving a pull request's code diff.

    This endpoint is temporary and is used to verify that our
    backend can successfully retrieve the actual code changes
    from GitHub.

    Later, this functionality will be called internally by the
    /review endpoint instead of being exposed separately.
    """

    # Ask the GitHub service to retrieve the PR diff.
    diff = await get_pull_request_diff(
        owner,
        repo,
        pull_number,
    )

    # Return the diff to the caller.
    return {
        "owner": owner,
        "repository": repo,
        "pull_number": pull_number,
        "diff": diff,
    }


@app.get("/github-test/{owner}/{repo}/{pull_number}/clean-diff")
async def clean_diff_test(
    owner: str,
    repo: str,
    pull_number: int,
):
    """
    Test endpoint that retrieves a GitHub PR diff and removes
    files that are not relevant for AI code review.
    """

    # Step 1:
    # Retrieve the original diff from GitHub.
    raw_diff = await get_pull_request_diff(
        owner,
        repo,
        pull_number,
    )

    # Step 2:
    # Remove irrelevant files from the diff.
    cleaned_diff = clean_diff(raw_diff)

    # Step 3:
    # Return both versions so we can compare them during testing.
    return {
        "raw_diff": raw_diff,
        "cleaned_diff": cleaned_diff,
    }