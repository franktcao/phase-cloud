import flask
import matplotlib.pyplot as plt
import pickle
from flask import (
    Flask,
    redirect,
    render_template,
    url_for,
)
from typing import Any, List
from wordcloud import WordCloud

from .model import predict
from .utils import upload_to_aws

app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY="\xe0\xcd\xac#\x06\xd9\xe4\x00\xa5\xf2\x88\xc3\xef$\xa5\x05n\x97\xd8"
)


@app.route("/", methods=("GET", "POST"))
def index():
    """
    Generate main page:
        * For GET requests, base.html will be rendered without any results shown
        * For POST requests, input text is extracted from the form in base.html.
    """
    if update_result():
        return redirect(url_for("result"))
    else:
        return render_template("base.html")


@app.route("/result", methods=("GET", "POST"))
def result():
    """
    Generate result page:
        * For GET requests, render result page with `message` from session
        * For POST requests, render result page with `message` from form on result page
    """
    if update_result():
        return redirect(url_for("result"))
    else:
        message = flask.session.get("message")
        fig = get_word_cloud_fig(text=message)
        fig.show()

        saved_image = "word_cloud.png"
        plt.savefig(saved_image)
        upload_to_aws(file_name="word_cloud.png", bucket="phrase-cloud")

        return render_template("result.html", message=message, image=saved_image)


def update_result() -> bool:
    """
    Update session's message and return whether or not to update result page with data
    from form.

    :return:
        Whether or not to update the result page with data from form
    """
    if flask.request.method == "POST":
        message = flask.request.form["message"]
        if message is not None:
            # Update session's message with the message from the form
            flask.session.clear()
            flask.session["message"] = message
            return True
    return False


def get_word_cloud_fig(
    text: str, fig_size: List[int] = [16, 12], **wc_kwargs: Any
) -> plt.Figure:
    """
    Generate and return a word cloud image.

    :param text:
        Text to be converted to a word cloud
    :param fig_size:
        Size of image figure
    :param wc_kwargs:
        Keyword arguments to initialize word cloud (see
        https://amueller.github.io/word_cloud/generated/wordcloud.WordCloud.html)
    :return:
        Image of word cloud
    """
    default_kwargs = dict(width=1280, height=960, background_color="white")
    wc_kwargs = {**default_kwargs, **wc_kwargs}

    cloud = WordCloud(**wc_kwargs).generate(text)

    fig, ax = plt.subplots(figsize=fig_size)
    ax.imshow(cloud, interpolation="bilinear")
    ax.axis("off")

    return fig
