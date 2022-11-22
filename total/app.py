from flask import Flask
from wsgiref.simple_server import make_server

from total.blueprint import api_blueprint
from total.blueprint import errors

app = Flask(__name__)

# app.register_blueprint(api_blueprint, url_prefix="")
# app.register_blueprint(errors, url_prefix="")
# app.run()


app.register_blueprint(api_blueprint, url_prefix="")
app.register_blueprint(errors, url_prefix="")
# app.run()
if __name__ == "__main__":
    app.run(debug=True)
# with make_server('', 5000, app) as server:
#     app.register_blueprint(api_blueprint, url_prefix="")
#     app.register_blueprint(errors, url_prefix="")
#     print("beb")
#     server.serve_forever()

