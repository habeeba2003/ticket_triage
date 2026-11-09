import re

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)

_lemmatizer = WordNetLemmatizer()
_NEGATIONS = {"no", "nor", "not"}
_STOP_WORDS = set(stopwords.words("english")) - _NEGATIONS


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s']", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def tokenize(text: str) -> list[str]:
    return text.split()


def remove_stop_words(tokens: list[str]) -> list[str]:
    return [t for t in tokens if t not in _STOP_WORDS]


def lemmatize(tokens: list[str]) -> list[str]:
    return [
        _lemmatizer.lemmatize(_lemmatizer.lemmatize(t, pos="v"), pos="n")
        for t in tokens
    ]


def preprocess(text: str) -> list[str]:
    return lemmatize(remove_stop_words(tokenize(clean_text(text))))