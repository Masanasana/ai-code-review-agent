"""FastAPI entry point for the AI Code Review Agent."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from httpx import HTTPStatusError

from app.agent.graph import review_graph
from app.models import ReviewRequest, ReviewResponse


app = FastAPI(
    title="AI Code Review Agent",
    description="AI-powered code review for public GitHub pull requests.",
    version="0.2.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://ai-code-review-agent-frontend.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "AI Code Review Agent API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/review", response_model=ReviewResponse)
async def review_pull_request(request: ReviewRequest):
    """Review any public GitHub pull request."""

    try:
        result = await review_graph.ainvoke(
            {"pr_url": str(request.pr_url)}
        )

        return {
            "review": result["review"],
            "github_review_url": result.get("github_review_url"),
            "github_review_posted": result.get("github_review_posted", False),
            "github_message": result.get(
                "github_message",
                "The AI review was completed.",
            ),
        }

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    except HTTPStatusError as exc:
        status = exc.response.status_code

        if status == 404:
            detail = "The GitHub pull request could not be found or is not publicly accessible."
        elif status == 403:
            detail = "GitHub rejected the request. The repository may be rate-limited or inaccessible."
        else:
            detail = f"GitHub returned HTTP {status} while retrieving the pull request."

        raise HTTPException(status_code=502, detail=detail) from exc

    except Exception as exc:
        print(f"Review error: {exc}")
        raise HTTPException(
            status_code=500,
            detail="The AI code review could not be completed.",
        ) from exc
