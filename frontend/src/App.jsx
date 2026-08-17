import { useState } from "react";
import "./App.css";


function App() {
  // GitHub PR URL entered by the user.
  const [prUrl, setPrUrl] = useState("");

  // Review returned by the FastAPI backend.
  const [reviewResult, setReviewResult] = useState(null);

  // Tracks whether a review is currently running.
  const [loading, setLoading] = useState(false);

  // Stores any error returned by the backend.
  const [error, setError] = useState("");


  async function handleReview() {
    // Clear previous results and errors.
    setReviewResult(null);
    setError("");

    // Validate that a URL was entered.
    if (!prUrl.trim()) {
      setError("Please enter a GitHub pull request URL.");
      return;
    }

    setLoading(true);

    try {
      // All AI and GitHub communication happens through
      // the backend. The frontend never calls Groq directly.
      const response = await fetch(
        "http://127.0.0.1:8000/review",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            pr_url: prUrl,
          }),
        }
      );


      if (!response.ok) {
        const errorData = await response.json();

        throw new Error(
          errorData.detail ||
          "Unable to review the pull request."
        );
      }


      const data = await response.json();

      setReviewResult(data);

    } catch (err) {
      setError(err.message);

    } finally {
      setLoading(false);
    }
  }


  return (
    <div className="app">

      {/* ================================================= */}
      {/* Header                                            */}
      {/* ================================================= */}

      <header className="header">

        <div className="header-content">

          <div className="brand">

            <div className="brand-icon">
              AI
            </div>

            <div>
              <h1>AI Code Review Agent</h1>

              <p>
                Intelligent pull request analysis powered by AI
              </p>
            </div>

          </div>

          <div className="status-indicator">
            <span className="status-dot"></span>
            Agent Online
          </div>

        </div>

      </header>


      {/* ================================================= */}
      {/* Main                                             */}
      {/* ================================================= */}

      <main className="main">


        {/* ------------------------------------------------ */}
        {/* Intro                                            */}
        {/* ------------------------------------------------ */}

        <section className="intro">

          <span className="eyebrow">
            AUTOMATED CODE REVIEW
          </span>

          <h2>
            Review a GitHub pull request
          </h2>

          <p>
            Enter a pull request URL and the agent will analyse
            the changed code for security vulnerabilities, bugs,
            performance issues and maintainability concerns.
          </p>

        </section>


        {/* ------------------------------------------------ */}
        {/* PR Input                                         */}
        {/* ------------------------------------------------ */}

        <section className="input-card">

          <label htmlFor="pr-url">
            Pull request URL
          </label>

          <div className="input-row">

            <input
              id="pr-url"
              type="url"
              placeholder="https://github.com/owner/repository/pull/123"
              value={prUrl}
              onChange={(event) =>
                setPrUrl(event.target.value)
              }
              disabled={loading}
            />

            <button
              onClick={handleReview}
              disabled={loading}
            >
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
            The agent retrieves the PR diff, analyses the changes
            and posts the review back to GitHub.
          </p>

        </section>


        {/* ================================================= */}
        {/* Loading                                          */}
        {/* ================================================= */}

        {loading && (

          <section className="loading-card">

            <div className="loading-icon">
              <div className="spinner"></div>
            </div>

            <div>

              <h3>
                Reviewing pull request
              </h3>

              <p>
                The AI agent is analysing the changed code.
              </p>

            </div>

          </section>

        )}


        {/* ================================================= */}
        {/* Error                                            */}
        {/* ================================================= */}

        {error && (

          <section className="error-card">

            <div className="error-icon">
              !
            </div>

            <div>

              <h3>
                Review failed
              </h3>

              <p>
                {error}
              </p>

            </div>

          </section>

        )}


        {/* ================================================= */}
        {/* Results                                          */}
        {/* ================================================= */}

        {reviewResult && (

          <section className="results">


            {/* -------------------------------------------- */}
            {/* Review overview                              */}
            {/* -------------------------------------------- */}

            <div className="results-header">

              <div>

                <span className="eyebrow">
                  REVIEW COMPLETE
                </span>

                <h2>
                  {reviewResult.review.summary}
                </h2>

              </div>


              <div
                className={`risk-badge risk-${reviewResult.review.overall_risk.toLowerCase()}`}
              >
                <span className="risk-dot"></span>

                {reviewResult.review.overall_risk.toUpperCase()}

                {" "}RISK
              </div>

            </div>


            {/* -------------------------------------------- */}
            {/* Review statistics                            */}
            {/* -------------------------------------------- */}

            <div className="stats">

              <div className="stat">

                <span className="stat-value">
                  {reviewResult.review.issues.length}
                </span>

                <span className="stat-label">
                  Issues identified
                </span>

              </div>


              <div className="stat">

                <span className="stat-value">
                  {
                    reviewResult.review.issues.filter(
                      (issue) =>
                        issue.severity.toLowerCase() ===
                        "critical"
                    ).length
                  }
                </span>

                <span className="stat-label">
                  Critical issues
                </span>

              </div>


              <div className="stat">

                <span className="stat-value">
                  {
                    reviewResult.review.issues.filter(
                      (issue) =>
                        issue.severity.toLowerCase() ===
                        "high"
                    ).length
                  }
                </span>

                <span className="stat-label">
                  High severity
                </span>

              </div>

            </div>


            {/* -------------------------------------------- */}
            {/* Issues                                       */}
            {/* -------------------------------------------- */}

            <div className="issues-section">

              <div className="section-heading">

                <div>
                  <span className="eyebrow">
                    FINDINGS
                  </span>

                  <h3>
                    Code review issues
                  </h3>
                </div>

              </div>


              {reviewResult.review.issues.length === 0 ? (

                <div className="no-issues">

                  <div className="success-icon">
                    ✓
                  </div>

                  <div>

                    <h3>
                      No significant issues identified
                    </h3>

                    <p>
                      The AI reviewer did not identify any
                      meaningful problems in the changed code.
                    </p>

                  </div>

                </div>

              ) : (

                <div className="issues-list">

                  {reviewResult.review.issues.map(
                    (issue, index) => (

                      <article
                        className="issue-card"
                        key={index}
                      >

                        <div className="issue-meta">

                          <span
                            className={`severity severity-${issue.severity.toLowerCase()}`}
                          >
                            {issue.severity}
                          </span>

                          <span className="category">
                            {issue.category}
                          </span>

                        </div>


                        <h4>
                          {issue.title}
                        </h4>


                        <div className="location">

                          <span>
                            {issue.file}
                          </span>

                          {issue.line !== null && (
                            <>
                              <span className="location-separator">
                                :
                              </span>

                              <span>
                                {issue.line}
                              </span>
                            </>
                          )}

                        </div>


                        <p className="description">
                          {issue.description}
                        </p>


                        <div className="recommendation">

                          <span className="recommendation-label">
                            RECOMMENDATION
                          </span>

                          <p>
                            {issue.recommendation}
                          </p>

                        </div>

                      </article>

                    )
                  )}

                </div>

              )}

            </div>


            {/* -------------------------------------------- */}
            {/* General recommendations                     */}
            {/* -------------------------------------------- */}

            {reviewResult.review.recommendations.length > 0 && (

              <div className="recommendations">

                <span className="eyebrow">
                  NEXT STEPS
                </span>

                <h3>
                  Recommendations
                </h3>

                <ul>

                  {reviewResult.review.recommendations.map(
                    (recommendation, index) => (

                      <li key={index}>
                        {recommendation}
                      </li>

                    )
                  )}

                </ul>

              </div>

            )}


            {/* -------------------------------------------- */}
            {/* GitHub CTA                                   */}
            {/* -------------------------------------------- */}

            <div className="github-cta">

              <div>

                <span className="eyebrow">
                  GITHUB
                </span>

                <h3>
                  Review posted successfully
                </h3>

                <p>
                  The AI-generated review has been posted
                  directly to the pull request.
                </p>

              </div>


              <a
                href={reviewResult.github_review_url}
                target="_blank"
                rel="noopener noreferrer"
              >
                View on GitHub
                <span> →</span>
              </a>

            </div>


          </section>

        )}

      </main>


      {/* ================================================= */}
      {/* Footer                                            */}
      {/* ================================================= */}

      <footer className="footer">

        <span>
          AI Code Review Agent
        </span>

        <span>
          FastAPI · LangGraph · Groq · GitHub
        </span>

      </footer>

    </div>
  );
}


export default App;