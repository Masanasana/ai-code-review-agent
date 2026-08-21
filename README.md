# AI Code Review Agent

An AI-powered GitHub Pull Request review agent that analyses changed code for **security vulnerabilities, bugs, performance problems, and maintainability issues**.

The application accepts **any public GitHub Pull Request URL**, retrieves the PR and diff, processes the changes, sends them to an LLM for structured analysis, and displays the resulting review in the web application. When the configured GitHub account has permission to review the repository, the application also posts the review directly to GitHub.

The project combines a React frontend, FastAPI backend, LangGraph orchestration, GitHub REST API integration, and Groq-hosted LLM inference.

---

## Overview

The AI Code Review Agent allows a developer to enter a public GitHub Pull Request such as:

```text
https://github.com/owner/repository/pull/123
```

The application then:

1. Validates and parses the GitHub Pull Request URL.
2. Identifies the repository owner, repository name, and PR number dynamically.
3. Verifies that the repository is public.
4. Retrieves Pull Request metadata from GitHub.
5. Retrieves the Pull Request diff.
6. Removes irrelevant generated files from the diff.
7. Sends the cleaned changes to the LLM.
8. Validates the AI response using a structured Pydantic schema.
9. Generates a structured code review.
10. Attempts to post the review to GitHub when the configured GitHub account has permission.
11. Returns the AI review to the frontend even when GitHub posting is not permitted.

### Public repository support

The application is **not tied to a specific GitHub repository**. Any public repository can be submitted for analysis.

For example:

```text
https://github.com/fastapi/fastapi/pull/123
https://github.com/pallets/flask/pull/456
https://github.com/owner/my-public-project/pull/12
```

The repository does not need to belong to the GitHub account configured in `GITHUB_TOKEN` for the application to read and analyse a public Pull Request.

### Reading vs posting reviews

Reading a public Pull Request and posting a review are separate operations.

```text
Public repository
      |
      v
Fetch PR + diff
      |
      v
   AI review
      |
      +----------------------+
      |                      |
      v                      v
Has GitHub permission?   No permission
      |                      |
      v                      v
Post review             Show AI review
      |                 in application
      v                      |
GitHub review URL       No GitHub URL
```

Therefore, a user can still receive an AI review even when the configured GitHub account does not have write/review permission on the repository.

---

## Architecture

```text
React UI
   |
   | HTTP POST /review
   v
FastAPI Backend
   |
   v
LangGraph Agent Workflow
   |
   +--------------------------> GitHub REST API
   |                               |
   |                               +--> PR metadata
   |                               |
   |                               +--> PR diff
   |
   v
Diff Processor
   |
   v
Groq LLM
(openai/gpt-oss-120b)
   |
   v
Structured CodeReview
(Pydantic)
   |
   v
GitHub Review Service
   |
   +--> Post review when permitted
   |
   +--> Otherwise return AI review only
   |
   v
React Frontend
```

### LangGraph workflow

```text
Pull Request URL
       |
       v
Parse GitHub URL
       |
       v
Validate public repository
       |
       v
Retrieve PR metadata
       |
       v
Retrieve PR diff
       |
       v
Clean diff
       |
       v
AI Code Review
       |
       v
Validate structured response
       |
       v
Format review
       |
       v
Attempt GitHub review
       |
       v
Return result to frontend
```

---

## Technology Stack

### Frontend

- React
- Vite
- JavaScript
- CSS

### Backend

- Python
- FastAPI
- Pydantic
- HTTPX

### AI / Agent

- LangGraph
- Groq
- OpenAI-compatible chat completion API
- `openai/gpt-oss-120b`

### Integration

- GitHub REST API

---

## Project Structure

```text
ai-code-review-agent/
|
├── backend/
│   ├── app/
│   │   ├── agent/
│   │   │   ├── graph.py              # LangGraph workflow
│   │   │   ├── nodes.py
│   │   │   └── prompts.py
│   │   │
│   │   ├── services/
│   │   │   ├── github.py              # GitHub API integration
│   │   │   ├── diff_processor.py      # Diff cleaning
│   │   │   ├── llm.py                 # LLM integration
│   │   │   └── review_formatter.py    # GitHub review formatting
│   │   │
│   │   ├── config.py                  # Environment configuration
│   │   ├── main.py                    # FastAPI application
│   │   └── models.py                  # Request/response schemas
│   │
│   ├── .env.example
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── main.jsx
│   ├── package.json
│   └── ...
│
├── Architecture_diagram.png
├── Architecture.txt
└── README.md
```

---

## Code Review Output

The AI reviewer returns a structured response similar to:

```json
{
  "summary": "Short summary of the pull request.",
  "overall_risk": "medium",
  "issues": [
    {
      "severity": "high",
      "category": "security",
      "file": "app/main.py",
      "line": 42,
      "title": "Potential security vulnerability",
      "description": "Explanation of the issue.",
      "recommendation": "Recommended remediation."
    }
  ],
  "recommendations": [
    "General recommendation."
  ]
}
```

### Supported severity levels

- `critical`
- `high`
- `medium`
- `low`

### Supported categories

- `security`
- `bug`
- `performance`
- `quality`
- `maintainability`
- `error_handling`

### Review principles

The AI reviewer focuses on meaningful engineering problems rather than stylistic preferences.

It primarily considers:

- Security vulnerabilities
- Hardcoded secrets and credential exposure
- Bugs and incorrect behaviour
- Reliability problems
- Performance problems
- Material maintainability issues
- Error handling problems
- Potential edge cases

The reviewer is instructed to:

- Only report issues supported by the provided diff.
- Avoid inventing problems.
- Use the exact file path from the diff.
- Avoid guessing line numbers.
- Avoid duplicate findings.
- Prioritise actionable issues.
- Distinguish real secrets from obvious placeholders.

For example, this is a placeholder and should not be treated as a leaked production credential:

```text
GITHUB_TOKEN=your_github_token_here
```

---

## Environment Variables

Create a `.env` file inside the `backend` directory.

```env
GROQ_API_KEY=your_groq_api_key_here
GITHUB_TOKEN=your_github_token_here
```

### `GROQ_API_KEY`

Required for AI-powered code review.

### `GITHUB_TOKEN`

Optional for reading public repositories, but recommended.

A GitHub token provides a higher API rate limit and allows the application to post reviews when the configured GitHub account has the necessary repository permissions.

The application does **not** require the configured GitHub account to own or collaborate on a public repository simply to analyse it.

Never commit the real `.env` file or API credentials to Git.

A template is provided at:

```text
backend/.env.example
```

---

## Running the Backend Locally

Navigate to the backend:

```bash
cd backend
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Running the Frontend Locally

Navigate to the frontend:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173
```

If the backend is running somewhere other than `http://localhost:8000`, configure the frontend API URL using its environment configuration.

---

## Using the Application

1. Start the FastAPI backend.
2. Start the React frontend.
3. Open the frontend in a browser.
4. Enter a public GitHub Pull Request URL.
5. Click **Review Pull Request**.
6. Wait for the AI agent to complete the analysis.
7. Review the findings displayed in the UI.
8. If the configured GitHub account has permission, use the GitHub link to view the posted review.

Example:

```text
https://github.com/owner/public-repository/pull/123
```

### Testing public repositories

To verify that public-repository support works independently of repository ownership, test with a public repository where the configured GitHub account does not have write access.

Expected behaviour:

```text
PR retrieved successfully
        |
        v
AI review generated successfully
        |
        v
Review displayed in frontend
```

GitHub posting may be unavailable in this case, but that should **not** cause the AI review itself to fail.

---

## API

### `POST /review`

Reviews a public GitHub Pull Request.

#### Request

```json
{
  "pr_url": "https://github.com/owner/repository/pull/123"
}
```

#### Response when the review is posted

```json
{
  "review": {
    "summary": "No significant issues were identified.",
    "overall_risk": "low",
    "issues": [],
    "recommendations": []
  },
  "github_review_url": "https://github.com/owner/repository/pull/123#pullrequestreview-...",
  "github_review_posted": true,
  "github_message": "The AI review was posted directly to GitHub."
}
```

#### Response when the review cannot be posted

```json
{
  "review": {
    "summary": "A potential security issue was identified.",
    "overall_risk": "high",
    "issues": [],
    "recommendations": []
  },
  "github_review_url": null,
  "github_review_posted": false,
  "github_message": "The pull request was reviewed successfully, but the configured GitHub account does not have permission to post a review on this repository."
}
```

The second response is still a **successful AI review**. GitHub write access is not required to analyse a public Pull Request.

---

## Error Handling

The application validates:

- GitHub Pull Request URLs
- GitHub repository visibility
- GitHub API responses
- AI-generated JSON
- AI response structure using Pydantic

Invalid or malformed AI responses are rejected during schema validation rather than being passed through to the frontend.

GitHub posting failures are handled separately from AI review failures so that lack of repository write access does not discard an otherwise successful review.

---

## Security Considerations

Secrets are kept outside the source code using environment variables.

The repository ignores:

```text
.env
.venv/
__pycache__/
*.pyc
```

### Never commit real credentials

Do not put real API keys, passwords, access tokens, database credentials, or cloud credentials into a Pull Request—even when testing the reviewer.

For security-testing purposes, use clearly fake values such as:

```python
def get_api_key():
    return "sk-test-123456789abcdef"


def get_database_password():
    return "MyFakePassword123!"
```

The purpose of the test is to verify that the AI reviewer identifies the pattern without exposing a real credential.

---

## Deployment

The backend can be deployed as a web service on **Render**.

Typical Render configuration:

```text
Service type: Web Service
Runtime: Python
Root directory: backend
```

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Configure the following environment variables in Render:

```text
GROQ_API_KEY
GITHUB_TOKEN
```

The frontend can be deployed separately as a Vite/React application and configured to point to the deployed FastAPI `/review` endpoint.

---

## Design Decisions

### Why FastAPI?

FastAPI provides a lightweight asynchronous API layer with automatic OpenAPI documentation and strong request/response validation through Pydantic.

### Why LangGraph?

LangGraph provides an explicit workflow structure for coordinating the individual steps of the code review process.

This makes it easier to extend the agent with additional capabilities such as:

- Static analysis tools
- Multiple review stages
- Human approval
- Additional AI agents
- Automated remediation

### Why separate services?

GitHub communication, diff processing, LLM communication, and review formatting are separated into individual services.

This reduces coupling between the API layer and external integrations.

### Why structured AI output?

Rather than returning free-form text, the AI response is validated against a Pydantic `CodeReview` schema.

This provides predictable output for both the frontend and GitHub review formatter.

### Why separate AI review from GitHub posting?

A public Pull Request can be read without having write access to the repository. Treating review generation and GitHub posting as separate operations allows the application to support **any public repository** while still posting reviews where the configured GitHub account has permission.

---

## Current Limitations

The current version is a working prototype and has several areas that can be improved.

Potential improvements include:

- Authentication for users of the application.
- Persistent review history.
- Database-backed review storage.
- More sophisticated diff parsing.
- Static analysis integration.
- Review comments attached directly to specific GitHub diff lines.
- Support for larger Pull Requests through diff chunking.
- Improved retry and rate-limit handling.
- Improved automated test coverage.
- Production monitoring and observability.
- Support for private repositories through user-authorised GitHub access.

---

## Future Improvements

### Multi-stage review

Use separate analysis stages for:

```text
Security
   |
   v
Correctness
   |
   v
Performance
   |
   v
Maintainability
   |
   v
Final Review
```

### Tool-assisted review

Integrate traditional static analysis tools alongside the LLM:

```text
GitHub Diff
    |
    +-- LLM Analysis
    |
    +-- Static Analysis
    |
    +-- Security Scanning
             |
             v
       Combined Review
```

### Automated remediation

Future versions could generate suggested patches for selected issues, subject to developer approval.

---

## Project Status

**Status: Working prototype**

The current implementation supports:

- Public GitHub Pull Request input
- Dynamic repository and PR parsing
- Public repository validation
- GitHub PR metadata retrieval
- GitHub PR diff retrieval
- Diff cleaning
- AI-powered code review
- Structured review generation
- LangGraph orchestration
- Optional GitHub review posting
- React frontend
- Frontend-to-backend communication
- Local development
- Render-compatible backend deployment

---

## License

This project is intended as a technical demonstration and portfolio/interview project.
