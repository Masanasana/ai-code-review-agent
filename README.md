# AI Code Review Agent

An AI-powered GitHub Pull Request code review agent that automatically analyses changed code, identifies meaningful engineering issues, and posts a structured review directly back to the GitHub Pull Request.

The application combines a React frontend, FastAPI backend, LangGraph orchestration, GitHub REST API integration, and Groq-hosted LLM inference.

## Overview

The AI Code Review Agent allows a developer to submit a GitHub Pull Request URL and receive an automated code review.

The agent:

1. Accepts a GitHub Pull Request URL.
2. Parses the repository and Pull Request information.
3. Retrieves the Pull Request metadata and code diff from GitHub.
4. Removes irrelevant generated files from the diff.
5. Sends the cleaned code changes to an LLM.
6. Validates the AI response against a structured Pydantic schema.
7. Generates a structured code review.
8. Posts the review directly to the GitHub Pull Request.
9. Returns the review and GitHub review URL to the frontend.

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
   +---------------------> GitHub API
   |                         |
   |                         v
   |                      PR Diff
   |
   v
Diff Processor
   |
   v
Groq LLM (GPT-OSS 120B)
   |
   v
CodeReview Pydantic Model
   |
   v
GitHub API - Post PR Review
```

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

## Project Structure

```text
ai-code-review-agent/
|
├── backend/
│   ├── app/
│   │   ├── agent/
│   │   │   ├── graph.py
│   │   │   ├── nodes.py
│   │   │   └── prompts.py
│   │   │
│   │   ├── services/
│   │   │   ├── github.py
│   │   │   ├── diff_processor.py
│   │   │   ├── llm.py
│   │   │   └── review_formatter.py
│   │   │
│   │   ├── config.py
│   │   ├── main.py
│   │   └── models.py
│   │
│   ├── .env.example
│   ├── requirements.txt
│   └── .gitignore
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── App.css
│   │
│   ├── package.json
│   └── ...
│
└── README.md
```

## Agent Workflow

```text
Pull Request URL
       |
       v
Parse GitHub URL
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
Post review to GitHub
       |
       v
Return result to frontend
```

This separates the workflow into independent steps, making the system easier to test, maintain, and extend.

## Code Review Output

The AI reviewer returns a structured response:

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

## AI Review Principles

The AI reviewer is instructed to focus on meaningful engineering problems rather than stylistic preferences.

The review primarily considers:

- Security vulnerabilities
- Bugs and incorrect behaviour
- Reliability problems
- Performance problems
- Material maintainability issues
- Error handling problems
- Potential edge cases

The reviewer is also instructed to:

- Only report issues supported by the provided diff.
- Avoid inventing problems.
- Use the exact file path from the diff.
- Avoid guessing line numbers.
- Avoid duplicate findings.
- Prioritise actionable issues.
- Distinguish actual secrets from placeholder values.

For example:

```text
GITHUB_TOKEN=your_github_token_here
```

is treated as a placeholder rather than a leaked credential.

## GitHub Integration

The backend communicates with GitHub through the GitHub REST API.

The application uses GitHub authentication to:

- Retrieve Pull Request metadata.
- Retrieve Pull Request diffs.
- Post AI-generated reviews.

The generated review is posted directly to the Pull Request as a GitHub review comment.

## Environment Variables

Create a `.env` file inside the `backend` directory.

```env
GITHUB_TOKEN=your_github_token_here
GROQ_API_KEY=your_groq_api_key_here
```

Never commit the real `.env` file or API credentials to Git.

A template is provided in:

```text
backend/.env.example
```

## Running the Backend

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
fastapi dev app/main.py
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

## Running the Frontend

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

The frontend will be available at:

```text
http://localhost:5173
```

## Using the Application

1. Start the FastAPI backend.
2. Start the React frontend.
3. Open the frontend in a browser.
4. Enter a GitHub Pull Request URL.
5. Click **Review Pull Request**.
6. Wait for the AI agent to complete the analysis.
7. Review the findings displayed in the UI.
8. Follow the GitHub review link to view the posted review.

Example:

```text
https://github.com/Masanasana/ai-code-review-agent/pull/5
```

## API

### `POST /review`

Reviews a GitHub Pull Request.

#### Request

```json
{
  "pr_url": "https://github.com/owner/repository/pull/123"
}
```

#### Response

```json
{
  "review": {
    "summary": "No significant issues were identified.",
    "overall_risk": "low",
    "issues": [],
    "recommendations": []
  },
  "github_review_url": "https://github.com/owner/repository/pull/123#pullrequestreview-..."
}
```

## Error Handling

The application validates:

- GitHub Pull Request URLs
- GitHub API responses
- AI-generated JSON
- AI response structure using Pydantic

Invalid or malformed AI responses are rejected during schema validation rather than being passed through to the frontend.

## Security Considerations

Secrets are kept outside the source code using environment variables.

The repository ignores:

```text
.env
.venv/
__pycache__/
*.pyc
```

The application also instructs the AI reviewer to distinguish between placeholder credentials and actual credentials committed to source code.

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

GitHub communication, diff processing, LLM communication and review formatting are separated into individual services.

This reduces coupling between the API layer and external integrations.

### Why structured AI output?

Rather than returning free-form text, the AI response is validated against a Pydantic `CodeReview` schema.

This provides predictable output for both the frontend and GitHub review formatter.

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
- Production deployment and monitoring.

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

This would allow the system to combine deterministic analysis with AI reasoning.

### Automated remediation

Future versions could generate suggested patches for selected issues, subject to developer approval.

## Project Status

**Current status: Working prototype**

The current implementation successfully supports:

- GitHub Pull Request input
- GitHub authentication
- Pull Request metadata retrieval
- Pull Request diff retrieval
- Diff cleaning
- AI-powered code review
- Structured review generation
- LangGraph orchestration
- GitHub review posting
- React frontend
- Frontend-to-backend communication
- End-to-end local execution

## License

This project is intended as a technical demonstration and portfolio/interview project.
