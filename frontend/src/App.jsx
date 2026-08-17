import { useState } from "react";
import "./App.css";


function App() {
  // Stores the GitHub pull request URL entered by the user.
  const [prUrl, setPrUrl] = useState("");

  // Stores the review returned by our FastAPI backend.
  const [reviewResult, setReviewResult] = useState(null);

  // Tracks whether a review request is currently running.
  const [loading, setLoading] = useState(false);

  // Stores an error message if the request fails.
  const [error, setError] = useState("");


  async function handleReview() {
    // Clear any previous result or error.
    setReviewResult(null);
    setError("");

    // Make sure the user actually entered a PR URL.
    if (!prUrl.trim()) {
      setError("Please enter a GitHub pull request URL.");
      return;
    }

    // Show the loading state.
    setLoading(true);

    try {
      // Send the PR URL to our FastAPI backend.
      //
      // IMPORTANT:
      // The frontend does NOT communicate with Groq or GitHub
      // directly. Everything goes through our backend.
      const response = await fetch("http://127.0.0.1:8000/review", {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          pr_url: prUrl,
        }),
      });


      // Check whether the backend returned an error.
      if (!response.ok) {
        const errorData = await response.json();

        throw new Error(
          errorData.detail || "Failed to review pull request."
        );
      }


      // Convert the backend response from JSON into
      // a JavaScript object.
      const data = await response.json();

      // Store the result so React can display it.
      setReviewResult(data);

    } catch (err) {
      // Display a user-friendly error message.
      setError(err.message);

    } finally {
      // Stop showing the loading state regardless of
      // whether the request succeeded or failed.
      setLoading(false);
    }
  }


  return (
    <div className="app">

      {/* -------------------------------------------------- */}
      {/* Header                                             */}
      {/* -------------------------------------------------- */}

      <header className="header">

        <div>
          <h1>AI Code Review Agent</h1>

          <p>
            Automatically review GitHub pull requests using AI.
          </p>
        </div>

      </header>


      {/* -------------------------------------------------- */}
      {/* Main content                                       */}
      {/* -------------------------------------------------- */}

      <main className="main">

        {/* PR URL input section */}
        <section className="review-form">

          <label htmlFor="pr-url">
            GitHub Pull Request URL
          </label>

          <div className="input-row">

            <input
              id="pr-url"
              type="url"
              placeholder="https://github.com/owner/repository/pull/123"
              value={prUrl}
              onChange={(event) => setPrUrl(event.target.value)}
              disabled={loading}
            />

            <button
              onClick={handleReview}
              disabled={loading}
            >
              {loading ? "Reviewing..." : "Review Pull Request"}
            </button>

          </div>

        </section>


        {/* ------------------------------------------------ */}
        {/* Loading message                                  */}
        {/* ------------------------------------------------ */}

        {loading && (
          <section className="status-card">

            <div className="spinner"></div>

            <div>
              <h2>Reviewing pull request</h2>

              <p>
                Fetching the GitHub changes and running the AI
                code review. This may take a moment.
              </p>
            </div>

          </section>
        )}


        {/* ------------------------------------------------ */}
        {/* Error message                                    */}
        {/* ------------------------------------------------ */}

        {error && (
          <section className="error-card">

            <h2>Review failed</h2>

            <p>{error}</p>

          </section>
        )}


        {/* ------------------------------------------------ */}
        {/* Review result                                    */}
        {/* ------------------------------------------------ */}

        {reviewResult && (
          <section className="review-result">

            {/* Summary */}
            <div className="review-header">

              <div>

                <span className="section-label">
                  AI CODE REVIEW
                </span>

                <h2>
                  {reviewResult.review.summary}
                </h2>

              </div>


              {/* Overall risk */}
              <div
                className={`risk-badge risk-${reviewResult.review.overall_risk.toLowerCase()}`}
              >
                {reviewResult.review.overall_risk.toUpperCase()} RISK
              </div>

            </div>


            {/* Issues */}
            <div className="issues-section">

              <h3>
                Issues ({reviewResult.review.issues.length})
              </h3>


              {reviewResult.review.issues.length === 0 ? (

                <div className="no-issues">

                  <h4>No significant issues identified</h4>

                  <p>
                    The AI reviewer did not identify any
                    meaningful problems in the changed code.
                  </p>

                </div>

              ) : (

                <div className="issues-list">

                  {reviewResult.review.issues.map((issue, index) => (

                    <article
                      className="issue-card"
                      key={index}
                    >

                      <div className="issue-top">

                        <span
                          className={`severity severity-${issue.severity.toLowerCase()}`}
                        >
                          {issue.severity.toUpperCase()}
                        </span>

                        <span className="category">
                          {issue.category}
                        </span>

                      </div>


                      <h4>
                        {issue.title}
                      </h4>


                      <p className="issue-location">

                        {issue.file}

                        {issue.line !== null &&
                          ` : ${issue.line}`}

                      </p>


                      <p>
                        {issue.description}
                      </p>


                      <div className="recommendation">

                        <strong>
                          Recommendation
                        </strong>

                        <p>
                          {issue.recommendation}
                        </p>

                      </div>

                    </article>

                  ))}

                </div>

              )}

            </div>


            {/* General recommendations */}
            {reviewResult.review.recommendations.length > 0 && (

              <div className="recommendations">

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


            {/* GitHub review link */}
            <div className="github-link">

              <a
                href={reviewResult.github_review_url}
                target="_blank"
                rel="noopener noreferrer"
              >
                View Review on GitHub →
              </a>

            </div>

          </section>
        )}

      </main>

    </div>
  );
}


export default App;