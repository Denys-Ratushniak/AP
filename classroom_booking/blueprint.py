import datetime
import json
import marshmallow
import sqlalchemy

from datetime import datetime
from flask_httpauth import HTTPBasicAuth
from flask_bcrypt import check_password_hash
from flask import Blueprint, jsonify, request, make_response
from classroom_booking import db_utils
from classroom_booking.models import User, Classroom, Order
from classroom_booking.schemas import (
    UserData,
    CreateUser,
    UpdateUser,
    GetUser,
    ClassroomData,
    CreateClassroom,
    OrderData,
    PlaceOrder,
    UpdateClassroom,
)

auth = HTTPBasicAuth()
api_blueprint = Blueprint('api', __name__)
errors = Blueprint('errors', __name__)


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


def status_response(response, code):
    param = response.json
    if isinstance(param, list):
        param.append({"code": code})
    else:
        param.update({"code": code})
    end_response = make_response(jsonify(param), code)
    return end_response


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


def admin_required(func):
    def wrapper(*args, **kwargs):
        username = auth.current_user()
        user = db_utils.get_entry_by_name(User, username)
        if user.isAdmin == '1':
            return func(*args, **kwargs)
        else:
            return status_response(jsonify({"error": f"User must be an admin to use {func.__name__}."}), 401)

    wrapper.__name__ = func.__name__
    return wrapper


@api_blueprint.route("/login")
@auth.verify_password
def login(username, password):
    if username == '0' or not db_utils.is_name_taken(User, username):
        return False

    user = db_utils.get_entry_by_name(User, username)
    if check_password_hash(user.password, password):
        return True

    return False


@api_blueprint.route("/user_login")
@auth.login_required()
def user_login():
    return status_response(jsonify({"message": "Successfully signed in"}), 200)


@api_blueprint.route('/user', methods=["POST"])
def create_user():
    user_data = CreateUser().load(request.json)

    if db_utils.is_name_taken(User, user_data["username"]):
        return status_response(jsonify({"error": "User with entered username already exists"}), 402)

    user = db_utils.create_entry(User, **user_data)
    return status_response(jsonify(UserData().dump(user)), 200)


@api_blueprint.route('/user/self', methods=["GET", "DELETE", "PUT"])
@auth.login_required
def user_self():
    username = auth.current_user()
    user = db_utils.get_entry_by_name(User, username)
    selfid = user.id
    if request.method == 'GET':
        user = db_utils.get_entry_by_id(User, selfid)
        return status_response(jsonify(UserData().dump(user)), 200)

    if request.method == 'DELETE':
        user = db_utils.get_entry_by_id(User, selfid)
        user_data = {"userStatus": '0',
                     "username": '0'}
        db_utils.update_entry(user, **user_data)
        return status_response(jsonify(UserData().dump(user)), 200)

    if request.method == 'PUT':
        user_data = UpdateUser().load(request.json)

        user = db_utils.get_entry_by_id(User, selfid)
        db_utils.update_entry(user, **user_data)

        return status_response(jsonify(GetUser().dump(user)), 200)


@api_blueprint.route('/user/<int:user_id>', methods=["GET"])
@auth.login_required
@admin_required
def get_user_by_id(user_id):
    user = db_utils.get_entry_by_id(User, user_id)
    return status_response(jsonify(GetUser().dump(user)), 200)


@api_blueprint.route('/user/<string:user_name>', methods=["DELETE", "GET"])
@auth.login_required
@admin_required
def user_admin(user_name):
    if request.method == 'DELETE':
        user = db_utils.get_entry_by_name(User, user_name)

        user_data = {"userStatus": '0',
                     "username": '0'}
        db_utils.update_entry(user, **user_data)

        return status_response(jsonify(GetUser().dump(user)), 200)

    if request.method == "GET":
        user = db_utils.get_entry_by_name(User, user_name)
        return status_response(jsonify(GetUser().dump(user)), 200)


@api_blueprint.route('/classroom', methods=["POST"])
@auth.login_required
@admin_required
def create_classroom():
    classroom_data = CreateClassroom().load(request.json)

    if db_utils.is_name_taken(Classroom, classroom_data["name"]):
        return status_response(jsonify({"error": "Classroom with entered name already exists"}), 403)

    user = db_utils.create_entry(Classroom, **classroom_data)
    return status_response(jsonify(ClassroomData().dump(user)), 200)


@api_blueprint.route('/classroom/findByStatus', methods=["POST"])
@auth.login_required
def find_classroom_by_status():
    if not validate_statuses(request.json["status"]):
        return status_response(jsonify({"error": "Invalid status value(s). "
                                                 "Should be list with maximum size = 2, "
                                                 "elements should be strings \'available' or 'unavailable' "}), 400)

    db_utils.reload_classroom_statuses()

    classrooms = db_utils.get_list_of_classrooms_by_1or2_statuses(request.json)
    ans = [ClassroomData().dump(x) for x in classrooms]

    return status_response(jsonify(ans), 200)


@api_blueprint.route('/classroom/<int:classroom_id>', methods=["GET", "PUT", "DELETE"])
@auth.login_required
@admin_required
def classroom(classroom_id):
    db_utils.reload_classroom_statuses()

    classroom = db_utils.get_entry_by_id(Classroom, classroom_id)

    if request.method == "GET":
        return status_response(jsonify(ClassroomData().dump(classroom)), 200)

    if request.method == "PUT":
        classroom_data = UpdateClassroom().load(request.json)
        db_utils.update_entry(classroom, **classroom_data)

        return status_response(jsonify(ClassroomData().dump(classroom)), 200)

    if request.method == "DELETE":
        db_utils.delete_entry(classroom)

        return status_response(jsonify({"message": "deleted"}), 200)


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
    #     return status_response({"error": "User with entered id does not found"}, 404)

    order_data = PlaceOrder().load(json.loads(paramjson))

    start_time = request.json['start_time']
    end_time = request.json['end_time']

    d1 = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    d2 = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")

    if d1 > d2:
        return status_response(jsonify({"error": "start_time must be earlier than end_time"}), 400)

    if (d2 - d1).seconds < 3600 or (d2 - d1).seconds > 5 * 24 * 3600:
        return status_response(jsonify({"error": "Booking time must be bigger or equal "
                                                 "than 1 hour and smaller or equal than 5 days"}), 400)

    if not db_utils.is_id_taken(Classroom, request.json['classroomId']):
        return status_response(jsonify({"error": "Classroom with entered id does not found"}), 404)

    if not db_utils.is_classroom_free_in_range(request.json['classroomId'], d1, d2):
        return status_response(jsonify({"error": "This classroom will be unavailable in entered period of time"}), 400)

    order_ = db_utils.create_order(**order_data)

    return status_response(jsonify(OrderData().dump(order_)), 200)


@api_blueprint.route('/booking/order/<int:order_id>', methods=["GET", "PUT"])
@auth.login_required
def order(order_id):
    db_utils.reload_classroom_statuses()

    order_ = db_utils.get_entry_by_id(Order, order_id)

    username = auth.current_user()
    user = db_utils.get_entry_by_name(User, username)
    selfid = user.id

    if selfid != order_.userId:
        return status_response(jsonify({"error": "This order is not yours"}), 402)

    if request.method == "GET":
        return status_response(jsonify(OrderData().dump(order_)), 200)

    if request.method == "PUT":
        order_data = {"orderStatus": "denied"}
        db_utils.update_entry(order_, **order_data)

        return status_response(jsonify(OrderData().dump(order_)), 200)


@api_blueprint.route('/booking/ordersby/me', methods=["GET"])
@auth.login_required
def get_self_orders():
    username = auth.current_user()
    db_utils.reload_classroom_statuses()
    user = db_utils.get_entry_by_name(User, username)
    userid = user.id
    orders = db_utils.find_orders_by_userid(userid)
    ans = [OrderData().dump(x) for x in orders]

    return status_response(jsonify(ans), 200)


@api_blueprint.route('/booking/ordersby/<int:userid>', methods=["GET"])
@auth.login_required
@admin_required
def get_all_orders(userid):
    if not db_utils.is_id_taken(User, userid):
        return status_response(jsonify({"error": "Not found"}), 404)

    orders = db_utils.find_orders_by_userid(userid)
    ans = [OrderData().dump(x) for x in orders]

    return status_response(jsonify(ans), 200)


@api_blueprint.route('/booking/findByStatus', methods=["GET"])
@auth.login_required
@admin_required
def get_orders_by_status():
    if not validate_statuses_orders(request.json["status"]):
        return status_response(jsonify({"error": "Invalid status value(s). "
                                                 "Should be list with maximum size = 2, "
                                                 "elements should be strings \'placed' or 'denied' "}), 400)

    orders = db_utils.get_list_of_orders_by_1or2_statuses(request.json)
    ans = [OrderData().dump(x) for x in orders]

    return status_response(jsonify(ans), 200)
