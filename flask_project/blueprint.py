from flask import Blueprint

api_blueprint = Blueprint('api', __name__)
StudentID = 7


@api_blueprint.route('/hello-world')
def hello_world_ex():
    return 'Hello World!'


@api_blueprint.route(f'/hello-world-{StudentID}')
def hello_world():
    return f'Hello World {StudentID}', 200