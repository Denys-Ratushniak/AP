from flask_bcrypt import generate_password_hash
from marshmallow import validate, Schema, fields
from datetime import date, datetime


class CreateUser(Schema):
    username = fields.String(required=True, validate=validate.Regexp('^[a-zA-Z][a-zA-Z\d\.-_]{4,120}$'))
    firstName = fields.String(required=True, validate=validate.Length(min=2))
    lastName = fields.String(required=True, validate=validate.Length(min=2))
    email = fields.String(required=True, validate=validate.Email())
    password = fields.Function(required=True, deserialize=lambda obj: generate_password_hash(obj), load_only=True)
    phone = fields.Function(validate=validate.Regexp('^[+]*[(]{0,1}[0-9]{1,4}[)]{0,1}[\s0-9]{4,20}$'))
    birthDate = fields.Date(validate=lambda x: x < date.today())


class UserData(Schema):
    id = fields.Integer()
    username = fields.String()
    firstName = fields.String()
    lastName = fields.String()
    email = fields.String()
    phone = fields.String()
    birthDate = fields.Date()
    isAdmin = fields.String()


class UpdateUser(Schema):
    firstName = fields.String(validate=validate.Length(min=2))
    lastName = fields.String(validate=validate.Length(min=2))
    email = fields.String(validate=validate.Email())
    password = fields.Function(deserialize=lambda obj: generate_password_hash(obj), load_only=True)
    phone = fields.Function(validate=validate.Regexp('^[+]*[(]{0,1}[0-9]{1,4}[)]{0,1}[\s0-9]{4,20}$'))


class GetUser(Schema):
    id = fields.Integer()
    username = fields.String()
    firstName = fields.String()
    lastName = fields.String()
    email = fields.String()
    phone = fields.String()
    birthDate = fields.Date()
    userStatus = fields.Integer()


class ClassroomData(Schema):
    id = fields.Integer()
    name = fields.String()
    classroomStatus = fields.String()
    capacity = fields.Integer()


class CreateClassroom(Schema):
    name = fields.String(required=True, validate=validate.Regexp('^[a-zA-Z\d\.-_]{1,120}$'))
    capacity = fields.Integer(required=True, validate=lambda x: x > 0)


class UpdateClassroom(Schema):
    name = fields.String(validate=validate.Regexp('^[a-zA-Z\d\.-_]{1,120}$'))
    capacity = fields.Integer(validate=lambda x: x > 0)


class OrderData(Schema):
    id = fields.Integer()
    classroomId = fields.Integer()
    userId = fields.Integer()
    start_time = fields.DateTime()
    end_time = fields.DateTime()
    orderStatus = fields.String()


class PlaceOrder(Schema):
    classroomId = fields.Integer(required=True)
    userId = fields.Integer(required=True)
    start_time = fields.DateTime(required=True, validate=lambda x: x >= datetime.now())
    end_time = fields.DateTime(required=True, validate=lambda x: x >= datetime.now())

