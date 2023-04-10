from flask import Flask

from flask_cors import CORS
app = Flask(__name__)
CORS(app)

from classroom_booking.blueprint import api_blueprint
from classroom_booking.blueprint import errors

app.register_blueprint(api_blueprint, url_prefix="")
app.register_blueprint(errors, url_prefix="")

if __name__ == "__main__":
    app.run(debug=True)
