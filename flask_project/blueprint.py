import datetime
from datetime import datetime
from flask_httpauth import HTTPBasicAuth
from flask_bcrypt import check_password_hash
from flask_login import logout_user
import json
import marshmallow
import sqlalchemy


from flask import Blueprint, jsonify, request, make_response
from lab7 import db_utils
from lab6.models import User, Classroom, Order
from lab7.schemas import (
    UserData,
    CreateUser,
    UpdateUser,
    GetUser,
    ClassroomData,
    CreateClassroom,
    OrderData,
    PlaceOrder,
    UpdateClassroom,
    UpdateOrder,
)


auth = HTTPBasicAuth()
api_blueprint = Blueprint('api', __name__)
StudentID = 7

errors = Blueprint('errors', __name__)


def verify_password(username, password):
    user = db_utils.get_entry_by_name(User, username)
    if check_password_hash(user.password, password):
        return username
    return None


def admin_required(func):
    def wrapper(*args, **kwargs):
        username = auth.current_user()
        user = db_utils.get_entry_by_name(User, username)
        if user.isAdmin == '1':
            return func(*args, **kwargs)
        else:
            return StatusResponse(jsonify({"error": f"User must be an admin to use {func.__name__}."}), 401)

    wrapper.__name__ = func.__name__
    return wrapper


@errors.app_errorhandler(sqlalchemy.exc.NoResultFound)
def handle_error(error):
    response = {
        'code': 404,
        'error': 'Not found'
    }

    return jsonify(response), 404


@errors.app_errorhandler(KeyError)
def handle_error(error):
    response = {
        'code': 400,
        'error': str(error.args[0]) + 'isnt presented in keys, add it or check existed one'
    }

    return jsonify(response), 400


@errors.app_errorhandler(sqlalchemy.exc.IntegrityError)
def handle_error(error):
    response = {
        'code': 400,
        'error': 'Not enough data'
    }

    return jsonify(response), 400


@errors.app_errorhandler(marshmallow.exceptions.ValidationError)
def handle_error(error):
    response = {
        'code': 400,
        'error': str(error.args[0])
    }

    return jsonify(response), 400


def StatusResponse(response, code):
    param = response.json
    if isinstance(param, list):
        param.append({"code": code})
    else:
        param.update({"code": code})
    end_response = make_response(jsonify(param), code)
    return end_response


@api_blueprint.route('/hello-world')
def hello_world_ex():
    return 'Hello World!'


def validate_statuses(statuses):
    if not isinstance(statuses, list) \
            or len(statuses) == 0 \
            or len(statuses) > 2:
        return False

    for x in statuses:
        if x != 'available' and x != 'unavailable':
            return False

    return True


def validate_statuses_orders(statuses):
    if not isinstance(statuses, list) \
            or len(statuses) == 0 \
            or len(statuses) > 2:
        return False

    for x in statuses:
        if x != 'placed' and x != 'denied':
            return False

    return True


@api_blueprint.route(f'/hello-world-{StudentID}')
def hello_world():
    return f'Hello World {StudentID}', 200


@api_blueprint.route('/user', methods=["POST"])
def create_user():
    user_data = CreateUser().load(request.json)
    if db_utils.is_name_taken(User, user_data["username"]):
        return StatusResponse(jsonify({"error": "User with entered username already exists"}), 402)

    user = None
    if request.authorization is not None:
        username = request.authorization.username
        password = request.authorization.password
        user = verify_password(username, password)
    if (request.authorization is None or user is None
            or db_utils.get_entry_by_name(User, username).isAdmin == '0') and \
            'isAdmin' in user_data.keys() and user_data['isAdmin'] == '1':
        return StatusResponse(jsonify({"error": "Only admins can create other admins"}), 405)

    user = db_utils.create_entry(User, **user_data)
    return StatusResponse(jsonify(UserData().dump(user)), 200)


@api_blueprint.route("/login")
@auth.verify_password
def login(username, password):
    user = db_utils.get_entry_by_name(User, username)
    print(user)
    if check_password_hash(user.password, password):
        return True

    return False


@api_blueprint.route('/user/<int:user_id>', methods=["GET"])
@auth.login_required
@admin_required
def get_user_by_id(user_id):
    user = db_utils.get_entry_by_id(User, user_id)
    return StatusResponse(jsonify(GetUser().dump(user)), 200)


@api_blueprint.route('/user/self', methods=["GET", "DELETE", "PUT"])
@auth.login_required
def user_self():
    username = auth.current_user()
    user = db_utils.get_entry_by_name(User, username)
    selfid = user.id
    if request.method == 'GET':
        user = db_utils.get_entry_by_id(User, selfid)
        return StatusResponse(jsonify(UserData().dump(user)), 200)

    if request.method == 'DELETE':
        user = db_utils.get_entry_by_id(User, selfid)
        user_data = {"userStatus": '0',
                     "username": '0'}
        db_utils.update_entry(user, **user_data)
        return StatusResponse(jsonify(UserData().dump(user)), 200)

    if request.method == 'PUT':
        user_data = UpdateUser().load(request.json)

        user = db_utils.get_entry_by_id(User, selfid)
        db_utils.update_entry(user, **user_data)

        return StatusResponse(jsonify(GetUser().dump(user)), 200)


@api_blueprint.route('/user/<string:user_name>', methods=["PUT", "DELETE", "GET"])
@auth.login_required
@admin_required
def user_admin(user_name):
    if request.method == 'PUT':  # must not be in the future, now is existing for test
        user_data = UpdateUser().load(request.json)

        user = db_utils.get_entry_by_name(User, user_name)
        db_utils.update_entry(user, **user_data)

        return StatusResponse(jsonify(GetUser().dump(user)), 200)

    if request.method == 'DELETE':
        user = db_utils.get_entry_by_name(User, user_name)

        user_data = {"userStatus": '0',
                     "username": '0'}
        db_utils.update_entry(user, **user_data)

        return StatusResponse(jsonify(GetUser().dump(user)), 200)

    if request.method == "GET":
        user = db_utils.get_entry_by_name(User, user_name)
        return StatusResponse(jsonify(GetUser().dump(user)), 200)


@api_blueprint.route('/classroom', methods=["POST"])
@auth.login_required
@admin_required
def create_classroom():
    classroom_data = CreateClassroom().load(request.json)

    if db_utils.is_name_taken(Classroom, classroom_data["name"]):
        return StatusResponse(jsonify({"error": "Classroom with entered name already exists"}), 402)

    user = db_utils.create_entry(Classroom, **classroom_data)
    return StatusResponse(jsonify(ClassroomData().dump(user)), 200)


@api_blueprint.route('/classroom/findByStatus', methods=["GET"])
@auth.login_required
def find_classroom_by_status():
    if not validate_statuses(request.json["status"]):
        return StatusResponse(jsonify({"error": "Invalid status value(s). "
                                                "Should be list with maximum size = 2, "
                                                "elements should be strings \'available' or 'unavailable' "}), 400)

    db_utils.reload_classroom_statuses()

    classrooms = db_utils.get_list_of_classrooms_by_1or2_statuses(request.json)
    ans = [ClassroomData().dump(x) for x in classrooms]

    return StatusResponse(jsonify(ans), 200)


@api_blueprint.route('/classroom/<int:classroom_id>', methods=["GET", "PUT", "DELETE"])
@auth.login_required
@admin_required
def classroom(classroom_id):
    db_utils.reload_classroom_statuses()

    classroom = db_utils.get_entry_by_id(Classroom, classroom_id)

    if request.method == "GET":
        return StatusResponse(jsonify(ClassroomData().dump(classroom)), 200)

    if request.method == "PUT":
        classroom_data = UpdateClassroom().load(request.json)
        db_utils.update_entry(classroom, **classroom_data)

        return StatusResponse(jsonify(ClassroomData().dump(classroom)), 200)

    if request.method == "DELETE":
        db_utils.delete_entry(classroom)

        return StatusResponse(jsonify({"message": "deleted"}), 200)


@api_blueprint.route('/booking/order', methods=["POST"])
@auth.login_required
def place_order():
    username = auth.current_user()
    db_utils.reload_classroom_statuses()
    user = db_utils.get_entry_by_name(User, username)
    selfid = user.id

    param = request.json
    param.update({"userId": selfid})
    paramjson = json.dumps(param)

    # if not db_utils.is_id_taken(User, request.json['userId']):
    #     return StatusResponse({"error": "User with entered id does not found"}, 404)

    order_data = PlaceOrder().load(json.loads(paramjson))

    start_time = request.json['start_time']
    end_time = request.json['end_time']

    d1 = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    d2 = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")

    if d1 > d2:
        return StatusResponse(jsonify({"error": "start_time must be earlier than end_time"}), 400)

    if (d2 - d1).seconds < 3600 or (d2 - d1).seconds > 5 * 24 * 3600:
        return StatusResponse(jsonify({"error": "Booking time must be bigger or equal "
                                                "than 1 hour and smaller or equal than 5 days"}), 400)

    if not db_utils.is_classroom_free_in_range(request.json['classroomId'], d1, d2):
        return StatusResponse(jsonify({"error": "This classroom will be unavailable in entered period of time"}), 400)

    if not db_utils.is_id_taken(Classroom, request.json['classroomId']):
        return StatusResponse(jsonify({"error": "Classroom with entered id does not found"}), 404)

    order_ = db_utils.create_order(**order_data)

    return StatusResponse(jsonify(OrderData().dump(order_)), 200)


@api_blueprint.route('/booking/order/<int:order_id>', methods=["GET", "PUT", "DELETE"])
@auth.login_required
def order(order_id):
    db_utils.reload_classroom_statuses()

    order_ = db_utils.get_entry_by_id(Order, order_id)

    username = auth.current_user()
    user = db_utils.get_entry_by_name(User, username)
    selfid = user.id

    if selfid != order_.userId:
        return StatusResponse(jsonify({"error": "this order is not yours"}), 402)

    if request.method == "GET":
        return StatusResponse(jsonify(OrderData().dump(order_)), 200)

    if request.method == "PUT":
        order_data = UpdateOrder().load(request.json)

        db_utils.update_entry(order_, **order_data)

        return StatusResponse(jsonify(OrderData().dump(order_)), 200)

    if request.method == "DELETE":
        db_utils.delete_entry(order_)

        return StatusResponse(jsonify({"message": "deleted"}), 200)


@api_blueprint.route('/booking/ordersby/<int:userid>', methods=["GET"])
@auth.login_required
@admin_required
def get_all_orders(userid):
    if not db_utils.is_id_taken(User, userid):
        return StatusResponse(jsonify({"error": "user with entered id does not found"}), 404)

    orders = db_utils.find_orders_by_userid(userid)
    ans = [OrderData().dump(x) for x in orders]

    return StatusResponse(jsonify(ans), 200)


@api_blueprint.route('/booking/inventory', methods=["GET"])
@auth.login_required
@admin_required
def get_orders_by_status():
    if not validate_statuses_orders(request.json["status"]):
        return StatusResponse(jsonify({"error": "Invalid status value(s). "
                                                "Should be list with maximum size = 2, "
                                                "elements should be strings \'placed' or 'denied' "}), 400)

    orders = db_utils.get_list_of_orders_by_1or2_statuses(request.json)
    ans = [OrderData().dump(x) for x in orders]

    return StatusResponse(jsonify(ans), 200)
