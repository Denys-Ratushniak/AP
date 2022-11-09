from flask_bcrypt import generate_password_hash
from marshmallow import validate, Schema, fields
from datetime import date


class CreateUser(Schema):
    username = fields.String(required=True, validate=validate.Regexp('^[a-zA-Z\d\.-_]{4,120}$'))
    firstName = fields.String(required=True, validate=validate.Length(min=2))
    lastName = fields.String(required=True, validate=validate.Length(min=2))
    email = fields.String(required=True, validate=validate.Email())
    password = fields.Function(required=True, deserialize=lambda obj: generate_password_hash(obj), load_only=True)
    phone = fields.Function(validate=validate.Regexp('^[+]*[(]{0,1}[0-9]{1,4}[)]{0,1}[\s0-9]{4,20}$'))
    birthDate = fields.Date(validate=lambda x: x < date.today())


class UserData(Schema):
    uid = fields.Integer()
    username = fields.String()
    firstName = fields.String()
    lastName = fields.String()
    email = fields.String()
    password = fields.String()
    phone = fields.String()
    birthDate = fields.Date()
    userStatus = fields.Integer()


class UpdateUser(Schema):
    firstName = fields.String(validate=validate.Length(min=2))
    lastName = fields.String(validate=validate.Length(min=2))
    email = fields.String(validate=validate.Email())
    password = fields.Function(deserialize=lambda obj: generate_password_hash(obj), load_only=True)
    phone = fields.Function(validate=validate.Regexp('^[+]*[(]{0,1}[0-9]{1,4}[)]{0,1}[\s0-9]{4,20}$'))


class GetUser(Schema):
    uid = fields.Integer()
    username = fields.String()
    firstName = fields.String()
    lastName = fields.String()
    email = fields.String()
    phone = fields.String()
    birthDate = fields.Date()
    userStatus = fields.Integer()


class ClassroomData(Schema):
    uid = fields.Integer()
    name = fields.String()
    classroomStatus = fields.String()
    capacity = fields.Integer()


class CreateClassroom(Schema):
    name = fields.String(required=True, validate=validate.Regexp('^[a-zA-Z\d\.-_]{1,120}$'))
    classroomStatus = fields.String(validate=validate.OneOf('available', 'unavailable'))
    capacity = fields.Integer(validate=lambda x: x > 0)


class UpdateClassroom(Schema):
    name = fields.String(validate=validate.Regexp('^[a-zA-Z\d\.-_]{1,120}$'))
    classroomStatus = fields.String()


class OrderData(Schema):
    uid = fields.Integer()
    # classroomId = fields.Nested(ClassroomData(only=("uid", )), many=True)
    # userId = fields.Nested(UserData(only=("uid", )), many=True)

    classroomId = fields.Integer()
    userId = fields.Integer()

    start_time = fields.DateTime()
    end_time = fields.DateTime()

    orderStatus = fields.String()


class PlaceOrder(Schema):
    # classroomId = fields.Nested(ClassroomData(only=("uid", )), required=True, many=True)
    # userId = fields.Nested(UserData(only=("uid", )), required=True, many=True)

    classroomId = fields.Integer(required=True)
    userId = fields.Integer(required=True)
    start_time = fields.DateTime(required=True)
    end_time = fields.DateTime(required=True)
    orderStatus = fields.String()


class UpdateOrder(Schema):
    orderStatus = fields.String(validate=validate.OneOf('placed', 'denied'))
