
"""
Main entry point for the AI Code Review Agent API.

This module creates the FastAPI application and defines
the initial API endpoints.
"""
from fastapi import FastAPI, HTTPException

# Import the Pydantic model used to validate incoming
# pull request requests.
from app.models import (
    CodeReview,
    ReviewRequest,
    ReviewResponse,
)
from app.agent.graph import review_graph
# Import our GitHub service function.
#
# The actual GitHub API communication is kept inside
# services/github.py rather than inside this file.
from app.services.github import (
    get_pull_request,
    get_pull_request_diff,
    parse_pull_request_url,
    post_pull_request_review,
)

from app.services.review_formatter import format_review_as_markdown

# Import the diff processor.
from app.services.diff_processor import clean_diff

from app.services.llm import review_code
from app.models import CodeReview, ReviewRequest
from app.config import settings

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
@app.post("/review", response_model=ReviewResponse)
async def review_pull_request(request: ReviewRequest):
    """
    Run the AI code review agent against a GitHub pull request.
    """

    # Create the initial state for the agent.
    initial_state = {
        "pr_url": str(request.pr_url),
    }

    # Execute the LangGraph workflow.
    result = await review_graph.ainvoke(
        initial_state
    )

    # Return the AI review and the GitHub review URL.
    return {
        "review": result["review"],
        "github_review_url": result["github_review_url"],
    }
# async def review_pull_request(request: ReviewRequest):
#     """
#     Review a GitHub pull request using the AI code review agent.

#     Workflow:

#         1. Parse the GitHub PR URL.
#         2. Retrieve the PR diff.
#         3. Clean the diff.
#         4. Send the cleaned diff to the AI model.
#         5. Return the structured AI review.
#     """

#     try:
#         # ---------------------------------------------------------
#         # Step 1: Parse the GitHub PR URL
#         # ---------------------------------------------------------

#         owner, repo, pull_number = parse_pull_request_url(
#             str(request.pr_url)
#         )

#         # ---------------------------------------------------------
#         # Step 2: Retrieve the pull request diff
#         # ---------------------------------------------------------

#         raw_diff = await get_pull_request_diff(
#             owner=owner,
#             repo=repo,
#             pull_number=pull_number,
#         )

#         # ---------------------------------------------------------
#         # Step 3: Clean the diff
#         # ---------------------------------------------------------

#         cleaned_diff = clean_diff(raw_diff)

#         # Make sure there is actually code to review.
#         if not cleaned_diff.strip():
#             raise HTTPException(
#                 status_code=400,
#                 detail="No reviewable source-code changes found in the pull request.",
#             )

#         # ---------------------------------------------------------
#         # Step 4: Send the diff to the AI reviewer
#         # ---------------------------------------------------------

#         review = await review_code(cleaned_diff)
    

#         # ---------------------------------------------------------
#         # Step 5: Convert the AI review into Markdown
#         # ---------------------------------------------------------

#         review_markdown = format_review_as_markdown(review)


#         # ---------------------------------------------------------
#         # Step 6: Post the review back to GitHub
#         # ---------------------------------------------------------

#         github_review = await post_pull_request_review(
#             owner=owner,
#             repo=repo,
#             pull_number=pull_number,
#             review_body=review_markdown,
#         )

#         # ---------------------------------------------------------
#         # Step 7: Return the structured review
#         # ---------------------------------------------------------

#         return {
#             "review": review,
#             "github_review_url": github_review["html_url"],
#         }

#     except HTTPException:
#         # Re-raise HTTP exceptions so FastAPI can return the
#         # correct status code and error message.
#         raise

#     except ValueError as exc:
#         # URL parsing errors are client-side input errors.
#         raise HTTPException(
#             status_code=400,
#             detail=str(exc),
#         ) from exc

#     except Exception as exc:
#         # Print the actual exception in the FastAPI terminal.
#         # This is useful during development and debugging.
#         print(f"Review error: {exc}")

#         # Re-raise the original exception so FastAPI prints
#         # the full traceback in the terminal.
#     raise

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

@app.post("/ai-test", response_model=CodeReview)
async def ai_test():
    """
    Test endpoint for the Groq AI integration.

    This endpoint uses a small hardcoded code example so that
    we can verify our AI connection before connecting it to
    the GitHub diff pipeline.
    """

    # Small intentionally vulnerable example.
    test_diff = """
diff --git a/app.py b/app.py
@@ -1,5 +1,6 @@

 def get_user(user_id):
+    password = "admin123"
     return database.get_user(user_id)
"""

    # Send the test code to the AI reviewer.
    review = await review_code(test_diff)

    # Convert the Pydantic model into JSON.
    return review

@app.get("/github-test/parse-url")
async def parse_url_test(pr_url: str):
    """
    Test endpoint for parsing a GitHub pull request URL.
    """

    owner, repo, pull_number = parse_pull_request_url(pr_url)

    return {
        "owner": owner,
        "repository": repo,
        "pull_number": pull_number,
    }


@app.get("/github-test/auth")
async def github_auth_test():
    """
    Test whether the configured GitHub token is valid.
    """

    import httpx

    headers = {
        "Authorization": f"Bearer {settings.github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2026-03-10",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.github.com/user",
            headers=headers,
        )

    response.raise_for_status()

    user = response.json()

    return {
        "github_username": user["login"],
        "authenticated": True,
    }