import flask
import pickle
from flask import (
    Flask,
    redirect,
    render_template,
    url_for,
)

from .model import predict

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
        df_pred = model.predict(model=model, text=message)
        sentiment = df_pred.head(1)["sentiment"].values[0]
        score = df_pred.head(1)["score"].values[0]

        return render_template(
            "result.html", message=message, sentiment=sentiment, score=score
        )


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
