from flask import Flask

app = Flask(__name__)
app.config.from_object('config')

from writing_center.views import View
View.register(app)

if __name__ == "__main__":
    app.run()
