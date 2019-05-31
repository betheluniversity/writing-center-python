from flask import Flask
from flask import session as flask_session
from datetime import datetime

app = Flask(__name__)
app.config.from_object('config')
app.debug = True

from writing_center.views import View
from writing_center.message_center import MessageCenterView
View.register(app)
MessageCenterView.register(app)


# This makes these variables open to use everywhere
@app.context_processor
def utility_processor():
    to_return = {}
    to_return.update({
        'now': datetime.now(),
    })

    return to_return


@app.before_request
def before_request():
    flask_session['NAME'] = app.config["TEST_NAME"]


if __name__ == "__main__":
    app.run()
