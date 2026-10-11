from typing import Literal
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = FastAPI(title="Batch Sentiment API")

# Allow browser-based evaluators to call this API from another origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize once at startup instead of once per sentence/request.
analyzer = SentimentIntensityAnalyzer()


class SentimentRequest(BaseModel):
    sentences: list[str] = Field(min_length=1)


class SentimentResult(BaseModel):
    sentence: str
    sentiment: Literal["happy", "sad", "neutral"]


class SentimentResponse(BaseModel):
    results: list[SentimentResult]


@app.get("/")
def root():
    return {"message": "Sentiment API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/sentiment", response_model=SentimentResponse)
def analyze_sentiment(request: SentimentRequest) -> SentimentResponse:
    results: list[SentimentResult] = []

    for sentence in request.sentences:
        score = analyzer.polarity_scores(sentence)["compound"]

        if score >= 0.05:
            sentiment = "happy"
        elif score <= -0.05:
            sentiment = "sad"
        else:
            sentiment = "neutral"

        results.append(SentimentResult(sentence=sentence, sentiment=sentiment))

    return SentimentResponse(results=results)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000")),
    )
