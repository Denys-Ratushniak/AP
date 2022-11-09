from flask import Flask
from wsgiref.simple_server import make_server

from blueprint import api_blueprint
from blueprint import errors

# from apscheduler.schedulers.background import BackgroundScheduler
#
# from lab7 import db_utils

# sched = BackgroundScheduler(daemon=True)
# sched.add_job(db_utils.reload_classroom_statuses, 'interval', seconds=30)
# sched.start()

app = Flask(__name__, instance_path="/B:/Projects/AP/flask_project/instance")

with make_server('', 5000, app) as server:
    app.register_blueprint(api_blueprint, url_prefix="")
    app.register_blueprint(errors, url_prefix="")
    server.serve_forever()
