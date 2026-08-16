# Import BaseModel for creating structured request/response models
# and HttpUrl for validating that a value is a valid HTTP/HTTPS URL.
from pydantic import BaseModel, HttpUrl


# Define the structure of the data that our /review endpoint expects.
# Pydantic will automatically validate the incoming request against this model.
class ReviewRequest(BaseModel):

    # The GitHub Pull Request URL that the user wants the AI agent to review.
    # HttpUrl ensures that the value is a properly formatted HTTP/HTTPS URL.
    pr_url: HttpUrl