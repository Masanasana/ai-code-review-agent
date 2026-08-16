"""
Diff processing service.

This module is responsible for cleaning and preparing a raw
GitHub pull request diff before it is sent to the AI model.

The GitHub API can return changes to files that are not useful
for an AI code review, such as:

    - Python __pycache__ files
    - .pyc compiled files
    - Binary files
    - Other generated files

We remove those files here so that the AI receives only
relevant source-code changes.
"""


# File extensions and directory patterns that we do not want
# to send to the AI model.
IGNORED_PATTERNS = (
    "__pycache__/",
    ".pyc",
    ".pyo",
    ".pyd",
)


def should_ignore_file(file_path: str) -> bool:
    """
    Determine whether a file should be excluded from the review.

    Parameters
    ----------
    file_path : str
        Path of the file inside the Git repository.

    Returns
    -------
    bool
        True if the file should be ignored, otherwise False.
    """

    # Check whether any of our ignored patterns appear in
    # the file path.
    for pattern in IGNORED_PATTERNS:

        if pattern in file_path:
            return True

    return False


def clean_diff(raw_diff: str) -> str:
    """
    Remove irrelevant files from a GitHub unified diff.

    The GitHub API returns one large string containing the
    changes for every file in the pull request.

    This function splits the diff into individual file sections,
    removes unwanted files, and combines the remaining sections.

    Parameters
    ----------
    raw_diff : str
        Raw unified diff returned by GitHub.

    Returns
    -------
    str
        Cleaned diff containing only relevant source-code changes.
    """

    # If GitHub returned an empty diff, return an empty string.
    if not raw_diff.strip():
        return ""

    # A Git diff starts a new file section with:
    #
    # diff --git a/file b/file
    #
    # Splitting on this marker allows us to process each changed
    # file independently.
    sections = raw_diff.split("diff --git ")

    cleaned_sections = []

    for section in sections:

        # The first section is normally empty because the diff
        # starts with "diff --git".
        if not section.strip():
            continue

        # The first line contains the paths of the old and new files.
        #
        # Example:
        #
        # a/app.py b/app.py
        #
        first_line = section.splitlines()[0]

        # Extract the new file path.
        #
        # We use the second path because that represents the
        # version of the file after the PR changes.
        parts = first_line.split()

        if len(parts) < 2:
            continue

        new_file_path = parts[1]

        # Remove the "b/" prefix from the path.
        new_file_path = new_file_path.removeprefix("b/")

        # Skip files that are not useful for code review.
        if should_ignore_file(new_file_path):
            continue

        # Keep the section because it represents a relevant
        # source-code change.
        cleaned_sections.append(
            "diff --git " + section
        )

    # Join all relevant file sections back together.
    return "\n".join(cleaned_sections)
