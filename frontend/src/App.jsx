import { useState } from "react";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL;

function App() {
  const [prUrl, setPrUrl] = useState("");
  const [reviewResult, setReviewResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleReview() {
    setReviewResult(null);
    setError("");

    if (!prUrl.trim()) {
      setError("Please enter a GitHub pull request URL.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/review`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ pr_url: prUrl.trim() }),
      });

      let data;
      try {
        data = await response.json();
      } catch {
        throw new Error("The backend returned an invalid response.");
      }

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to review the pull request."
        );
      }

      setReviewResult(data);
    } catch (err) {
      setError(err.message || "Unable to review the pull request.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div className="brand">
            <div className="brand-icon">AI</div>
            <div>
              <h1>AI Code Review Agent</h1>
              <p>Intelligent pull request analysis powered by AI</p>
            </div>
          </div>

          <div className="status-indicator">
            <span className="status-dot"></span>
            Agent Online
          </div>
        </div>
      </header>

      <main className="main">
        <section className="intro">
          <span className="eyebrow">AUTOMATED CODE REVIEW</span>
          <h2>Review any public GitHub pull request</h2>
          <p>
            Enter a public pull request URL and the agent will analyse the
            changed code for security vulnerabilities, bugs, performance
            issues and maintainability concerns.
          </p>
        </section>

        <section className="input-card">
          <label htmlFor="pr-url">Pull request URL</label>

          <div className="input-row">
            <input
              id="pr-url"
              type="url"
              placeholder="https://github.com/owner/repository/pull/123"
              value={prUrl}
              onChange={(event) => setPrUrl(event.target.value)}
              disabled={loading}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  handleReview();
                }
              }}
            />

            <button onClick={handleReview} disabled={loading}>
              {loading ? (
                <>
                  <span className="button-spinner"></span>
                  Reviewing
                </>
              ) : (
                "Review Pull Request"
              )}
            </button>
          </div>

          <p className="input-help">
            Public repositories do not need to belong to your GitHub account.
            The AI review can be displayed even when the app cannot post back
            to the repository.
          </p>
        </section>

        {loading && (
          <section className="loading-card">
            <div className="loading-icon">
              <div className="spinner"></div>
            </div>
            <div>
              <h3>Reviewing pull request</h3>
              <p>The AI agent is analysing the changed code.</p>
            </div>
          </section>
        )}

        {error && (
          <section className="error-card">
            <div className="error-icon">!</div>
            <div>
              <h3>Review failed</h3>
              <p>{error}</p>
            </div>
          </section>
        )}

        {reviewResult && (
          <section className="results">
            <div className="results-header">
              <div>
                <span className="eyebrow">REVIEW COMPLETE</span>
                <h2>{reviewResult.review.summary}</h2>
              </div>

              <div
                className={`risk-badge risk-${reviewResult.review.overall_risk.toLowerCase()}`}
              >
                <span className="risk-dot"></span>
                {reviewResult.review.overall_risk.toUpperCase()} RISK
              </div>
            </div>

            <div className="stats">
              <div className="stat">
                <span className="stat-value">
                  {reviewResult.review.issues.length}
                </span>
                <span className="stat-label">Issues identified</span>
              </div>

              <div className="stat">
                <span className="stat-value">
                  {reviewResult.review.issues.filter(
                    (issue) => issue.severity.toLowerCase() === "critical"
                  ).length}
                </span>
                <span className="stat-label">Critical issues</span>
              </div>

              <div className="stat">
                <span className="stat-value">
                  {reviewResult.review.issues.filter(
                    (issue) => issue.severity.toLowerCase() === "high"
                  ).length}
                </span>
                <span className="stat-label">High severity</span>
              </div>
            </div>

            <div className="issues-section">
              <div className="section-heading">
                <div>
                  <span className="eyebrow">FINDINGS</span>
                  <h3>Code review issues</h3>
                </div>
              </div>

              {reviewResult.review.issues.length === 0 ? (
                <div className="no-issues">
                  <div className="success-icon">✓</div>
                  <div>
                    <h3>No significant issues identified</h3>
                    <p>
                      The AI reviewer did not identify any meaningful problems
                      in the changed code.
                    </p>
                  </div>
                </div>
              ) : (
                <div className="issues-list">
                  {reviewResult.review.issues.map((issue, index) => (
                    <article className="issue-card" key={index}>
                      <div className="issue-meta">
                        <span
                          className={`severity severity-${issue.severity.toLowerCase()}`}
                        >
                          {issue.severity}
                        </span>
                        <span className="category">{issue.category}</span>
                      </div>

                      <h4>{issue.title}</h4>

                      <div className="location">
                        <span>{issue.file}</span>
                        {issue.line !== null && (
                          <>
                            <span className="location-separator">:</span>
                            <span>{issue.line}</span>
                          </>
                        )}
                      </div>

                      <p className="description">{issue.description}</p>

                      <div className="recommendation">
                        <span className="recommendation-label">
                          RECOMMENDATION
                        </span>
                        <p>{issue.recommendation}</p>
                      </div>
                    </article>
                  ))}
                </div>
              )}
            </div>

            {reviewResult.review.recommendations.length > 0 && (
              <div className="recommendations">
                <span className="eyebrow">NEXT STEPS</span>
                <h3>Recommendations</h3>
                <ul>
                  {reviewResult.review.recommendations.map(
                    (recommendation, index) => (
                      <li key={index}>{recommendation}</li>
                    )
                  )}
                </ul>
              </div>
            )}

            <div
              className={`github-cta ${
                reviewResult.github_review_posted
                  ? "github-success"
                  : "github-info"
              }`}
            >
              <div>
                <span className="eyebrow">GITHUB</span>
                <h3>
                  {reviewResult.github_review_posted
                    ? "Review posted successfully"
                    : "AI review completed"}
                </h3>
                <p>{reviewResult.github_message}</p>
              </div>

              {reviewResult.github_review_url && (
                <a
                  href={reviewResult.github_review_url}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  View on GitHub <span>→</span>
                </a>
              )}
            </div>
          </section>
        )}
      </main>

      <footer className="footer">
        <span>AI Code Review Agent</span>
        <span>FastAPI · LangGraph · Groq · GitHub</span>
      </footer>
    </div>
  );
}

export default App;
