import numpy as np
import pandas as pd
import re
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import LogisticRegression


# Uncomment the below command to download the nltk wordnet data if you run locally!
# Heroku will download the wordnet vocabulary automatically using nltk.txt
# import nltk
# nltk.download('wordnet')


def preprocess(text: str) -> str:
    """
    Preprocess input text with sequential steps:
        1. List of stop words to be used, we can either hardcode the stopwords in the
           code or use stopwords from nltk, remember to exclude words like 'not', 'nor',
           and etc as it will affect the meaning significantly!
        2. The stop words will be removed from the preprocessed message
        3. Message will then be lemmatized (e.g. ran, run, runs, running -> run)

    :param text:
        Input text to convert to preprocess for phrase cloud
    :return:
        Preprocessed text for phrase cloud
    """
    text = text.lower()

    # Remove all website prefixes
    text = re.sub("((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))", "", text)

    # Remove user-mentions and hashtags
    text = re.sub("@[^\s]+", "", text)
    text = re.sub("#([^\s]+)", "", text)

    # Remove special characters (anything that is not alphanumeric, space, or tab)
    text = re.sub("[^0-9A-Za-z \t]", " ", text)
    # Truncate extended words like "heyyy" or "youuuu" into "heyy" and "youu",
    # respectively, only keep the last 2 characters
    text = re.sub(r"(.)\1\1+", r"\1\1", text)

    # Remove trailing characters from both front and back
    text = text.strip()

    # Create a list of stop words
    # fmt: off
    stop_words = [
        "a", "about", "above", "after", "again", "ain", "all", "am", "an", "and", "any",
        "are", "as", "at", "be", "because", "been", "before", "being", "below",
        "between", "both", "by", "can", "d", "did", "do", "does", "doing", "down",
        "during", "each", "few", "for", "from", "further", "had", "has", "have",
        "having", "he", "her", "here", "hers", "herself", "him", "himself", "his",
        "how", "i", "if", "in", "into", "is", "it", "its", "itself", "just", "ll", "m",
        "ma", "me", "more", "most", "my", "myself", "now", "o", "of", "on", "once",
        "only", "or", "other", "our", "ours", "ourselves", "out", "own", "re", "s",
        "same", "she", "shes", "should", "shouldve", "so", "some", "such", "t", "than",
        "that", "thatll", "the", "their", "theirs", "them", "themselves", "then",
        "there", "these", "they", "this", "those", "through", "to", "too", "under",
        "until", "up", "ve", "very", "was", "we", "were", "what", "when", "where",
        "which", "while", "who", "whom", "why", "will", "with", "won", "y", "you",
        "youd", "youll", "youre", "youve", "your", "yours", "yourself", "yourselves",
    ]
    # fmt: on

    lemmatizer = WordNetLemmatizer()
    tokens = []
    for token in text.split():
        if token not in stop_words:
            tokens.append(lemmatizer.lemmatize(token))
    return " ".join(tokens)


def predict(
    model: LogisticRegression,
    text: str,
    vectoriser: HashingVectorizer = HashingVectorizer(ngram_range=(1, 2)),
) -> pd.DataFrame:
    """
    Predict the sentiment of message, return a dataframe with columns:
        * text: str
        * sentiment: float
        * score: float
    In succession,
        1. Preprocess `text`
        2. Vectorize preprocessed `text` with vectorizer model
        3. Predict the sentiment with `model` from vectorized `text`
        4. Obtain sentiment score for whether text has positive or negative sentiment
    """
    textdata = vectoriser.transform([preprocess(text)])
    sentiment = model.predict(textdata)
    score = round(np.amax(model.predict_proba(textdata)), 3)

    data = [(text, sentiment, score)]
    df = pd.DataFrame(data, columns=["text", "sentiment", "score"])
    df["sentiment"] = df["sentiment"].replace([0, 1], ["Negative", "Positive"])

    return df
