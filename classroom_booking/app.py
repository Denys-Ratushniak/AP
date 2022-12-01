from flask import Flask
from classroom_booking.blueprint import api_blueprint
from classroom_booking.blueprint import errors

app = Flask(__name__)

app.register_blueprint(api_blueprint, url_prefix="")
app.register_blueprint(errors, url_prefix="")

if __name__ == "__main__":
    app.run(debug=True)
