import re
from typing import List

from fastapi import FastAPI, Request, Response
from pydantic import BaseModel

app = FastAPI()

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "*",
}


@app.middleware("http")
async def add_cors(request: Request, call_next):
    if request.method == "OPTIONS":
        return Response(status_code=204, headers=CORS_HEADERS)
    response = await call_next(request)
    for k, v in CORS_HEADERS.items():
        response.headers[k] = v
    return response


HAPPY = {
    "love", "loved", "loves", "loving", "great", "awesome", "amazing", "fantastic",
    "wonderful", "excellent", "happy", "glad", "joy", "joyful", "delighted", "thrilled",
    "excited", "good", "best", "perfect", "brilliant", "superb", "pleased", "enjoy",
    "enjoyed", "enjoying", "fun", "beautiful", "nice", "yay", "hooray", "congratulations",
    "celebrate", "celebrating", "cheerful", "grateful", "thankful", "proud", "smile",
    "smiling", "laugh", "laughing", "won", "win", "lovely", "terrific", "ecstatic",
    "overjoyed", "blessed", "impressed", "recommend", "favorite", "favourite", "like",
    "liked", "pleasant", "magnificent", "stoked", "elated", "satisfied", "relieved",
}
SAD = {
    "sad", "terrible", "awful", "horrible", "hate", "hated", "hates", "bad", "worst",
    "angry", "upset", "cry", "crying", "cried", "depressed", "miserable", "unhappy",
    "disappointed", "disappointing", "heartbroken", "lonely", "grief", "grieving",
    "lost", "loss", "died", "death", "sorrow", "tragic", "tragedy", "painful", "hurt",
    "hurts", "disgusting", "pathetic", "worthless", "hopeless", "devastated", "gloomy",
    "sorry", "regret", "tears", "miss", "missing", "failed", "failure", "annoying",
    "frustrated", "frustrating", "poor", "dreadful", "useless", "broken", "ruined",
    "stressed", "anxious", "afraid", "scared", "fear", "dislike", "disliked", "mourning",
    "down", "blue", "gutted", "furious", "mad", "wrong", "sick", "tired", "exhausted",
}
NEGATORS = {"not", "no", "never", "n't", "cannot", "hardly", "without", "isnt", "wasnt",
            "dont", "didnt", "doesnt", "cant", "wont", "aint"}
INTENS = {"very", "really", "so", "extremely", "absolutely", "totally", "incredibly"}


def classify(text: str) -> str:
    t = text.lower().replace("’", "'")
    t = re.sub(r"(\w)n't", r"\1 not", t)
    tokens = re.findall(r"[a-z']+", t)
    score = 0.0
    for i, w in enumerate(tokens):
        s = 1 if w in HAPPY else -1 if w in SAD else 0
        if not s:
            continue
        window = tokens[max(0, i - 3):i]
        if any(x in NEGATORS for x in window):
            s = -s
        if any(x in INTENS for x in window):
            s *= 1.5
        score += s
    score += 0.5 * t.count("!") * (1 if score > 0 else -1 if score < 0 else 0)
    if text.count("😊") + text.count("😀") + text.count("❤") + text.count("😍"):
        score += 1
    if text.count("😢") + text.count("😭") + text.count("😞"):
        score -= 1
    if score > 0:
        return "happy"
    if score < 0:
        return "sad"
    return "neutral"


class Body(BaseModel):
    sentences: List[str]


@app.get("/")
def health():
    return {"status": "ok", "usage": "POST /sentiment {sentences: [...]}"}


@app.post("/")
@app.post("/sentiment")
@app.post("/sentiment/")
def sentiment(body: Body):
    return {"results": [{"sentence": s, "sentiment": classify(s)} for s in body.sentences]}
