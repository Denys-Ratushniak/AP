import base64
import unittest
from unittest.mock import ANY

from flask import url_for, Flask
from flask_bcrypt import generate_password_hash
from flask_testing import TestCase

from total import db_utils
from total.models import User, Session, Order, Classroom, BaseModel, engine
from total.app import app


class BaseTestCase(TestCase):
    def setUp(self):
        self.create_tables()

        self.user1_data = {
            "username": "user1",
            "firstName": "user1",
            "lastName": "user1",
            "email": "user1@gmail.com",
            "password": "user1",
            "phone": "+380961010101",
            "birthDate": "2000-01-01",
            "isAdmin": "1"
        }

        self.user1_data_hashed = {
            **self.user1_data,
            "password": generate_password_hash(self.user1_data["password"]).decode("utf-8"),
        }

        self.user1_credentials = {
            "username": self.user1_data["username"],
            "password": self.user1_data["password"],
        }

        self.user2_data = {
            "username": "user2",
            "firstName": "user2",
            "lastName": "user2",
            "email": "user2@gmail.com",
            "password": "user2",
            "phone": "+380961010101",
            "birthDate": "2000-01-01",
            "isAdmin": "0"
        }

        self.update_user_valid = {
            "firstName": "changed",
            "lastName": "changed",
            "email": "changed@gmail.com",
            "password": "user0",
            "phone": "+380999999999",
        }

        self.update_user_invalid_firstname = {
            "firstName": "1",
        }

        self.update_user_valid_hashed = {
            **self.update_user_valid,
            "password": generate_password_hash(self.update_user_valid["password"]).decode("utf-8"),
        }

        self.user2_data_hashed = {
            **self.user2_data,
            "password": generate_password_hash(self.user2_data["password"]).decode("utf-8"),
        }

        self.user2_credentials = {
            "username": self.user2_data["username"],
            "password": self.user2_data["password"],
        }

        self.classroom1_data = {
            "name": "101",
            "capacity": 11
        }

        self.classroom1_update_data = {
            "name": "303",
        }

        self.classroom2_data = {
            "name": "202",
            "capacity": 22
        }

        self.classroom_2statuses = {
            "status": ['available', 'unavailable']
        }
        self.classroom_invalid_statuses = {
            "status": ['available', 'wrong_status']
        }

        self.order1_data = {
            "classroomId": 1,
            "start_time": "2022-12-21 12:00:00",
            "end_time": "2022-12-21 13:00:00"
        }

        self.order1_data_with_userid = {
            "classroomId": 1,
            "userId": 1,
            "start_time": "2022-12-21 12:00:00",
            "end_time": "2022-12-21 13:00:00"
        }

        self.order2_data = {
            "classroomId": 2,
            "start_time": "2022-12-22 12:00:00",
            "end_time": "2022-12-22 13:00:00"
        }

        self.order2_data_with_userid = {
            "classroomId": 2,
            "userId": 2,
            "start_time": "2022-12-22 12:00:00",
            "end_time": "2022-12-22 13:00:00"
        }

        self.order_2statuses = {
            "status": ['placed', 'denied']
        }
        self.order_invalid_statuses = {
            "status": ['lol', 'xd']
        }

    def tearDown(self):
        self.close_session()

    def create_tables(self):
        BaseModel.metadata.drop_all(engine)
        BaseModel.metadata.create_all(engine)

    def close_session(self):
        Session.close()

    def create_app(self):
        return app

    def get_auth_basic(self, credentials):
        to_token = credentials["username"] + ':' + credentials["password"]

        valid_credentials = base64.b64encode(to_token.encode()).decode("utf-8")

        return {'Authorization': 'Basic ' + str(valid_credentials)}


class TestUserSelf(BaseTestCase):
    def test_user_self_get(self):
        db_utils.create_entry(User, **self.user1_data_hashed)
        resp = self.client.get(
            url_for("api.user_self"),
            headers=self.get_auth_basic(self.user1_credentials)
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {
            "username": self.user1_data["username"],
            "firstName": self.user1_data["firstName"],
            "lastName": self.user1_data["lastName"],
            "email": self.user1_data["email"],
            "password": self.user1_data_hashed["password"],
            "phone": self.user1_data["phone"],
            "birthDate": self.user1_data["birthDate"],
            "isAdmin": self.user1_data["isAdmin"],
            "userStatus": 1,
            "code": 200,
        })

    def test_user_self_update(self):
        db_utils.create_entry(User, **self.user1_data_hashed)
        resp = self.client.put(
            url_for("api.user_self"),
            headers=self.get_auth_basic(self.user1_credentials),
            json=self.update_user_valid
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {
            "username": self.user1_data["username"],
            "firstName": self.update_user_valid["firstName"],
            "lastName": self.update_user_valid["lastName"],
            "email": self.update_user_valid["email"],
            "phone": self.update_user_valid["phone"],
            "birthDate": self.user1_data["birthDate"],
            "isAdmin": self.user1_data["isAdmin"],
            "userStatus": 1,
            "code": 200,
        })

    def test_user_self_delete(self):
        db_utils.create_entry(User, **self.user1_data_hashed)
        resp = self.client.delete(
            url_for("api.user_self"),
            headers=self.get_auth_basic(self.user1_credentials),
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {
            "username": "0",
            "firstName": self.user1_data["firstName"],
            "lastName": self.user1_data["lastName"],
            "email": self.user1_data["email"],
            "phone": self.user1_data["phone"],
            "password": self.user1_data_hashed["password"],
            "birthDate": self.user1_data["birthDate"],
            "isAdmin": self.user1_data["isAdmin"],
            "userStatus": 0,
            "code": 200,
        })

    def test_user_self_put_wrong_firstName(self):
        db_utils.create_entry(User, **self.user1_data_hashed)
        resp = self.client.put(
            url_for("api.user_self"),
            headers=self.get_auth_basic(self.user1_credentials),
            json=self.update_user_invalid_firstname
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json, {
            "code": 400,
            "error": "{'firstName': ['Shorter than minimum length 2.']}"
        })

    def test_unauth_not_existing_username(self):
        resp = self.client.get(url_for("api.user_self"))
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json, {'code': 404, 'error': 'Not found'})

    def test_unauth_wrong_password(self):
        db_utils.create_entry(User, **self.user1_data_hashed)
        resp = self.client.get(
            url_for("api.user_self"),
            headers=self.get_auth_basic({"username": self.user1_credentials["username"],
                                         "password": "invalid_password"})
        )
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(str(resp), "<WrapperTestResponse streamed [401 UNAUTHORIZED]>")


class TestCreateUser(BaseTestCase):
    def test_create_user(self):
        resp = self.client.post(
            url_for("api.create_user"),
            json=self.user2_data
        )
        self.assertEqual(resp.status_code, 200)

        self.assertEqual(resp.json, {
            "username": self.user2_data["username"],
            "firstName": self.user2_data["firstName"],
            "lastName": self.user2_data["lastName"],
            "email": self.user2_data["email"],
            "password": ANY,
            "phone": self.user2_data["phone"],
            "birthDate": self.user2_data["birthDate"],
            "isAdmin": self.user2_data["isAdmin"],
            "userStatus": 1,
            "code": 200,
        })
        self.assertTrue(
            Session.query(User).filter_by(username=self.user2_data["username"]).one()
        )


class TestGetUserById(BaseTestCase):
    def test_get_user_by_id(self):
        db_utils.create_entry(User, **self.user1_data_hashed)
        resp = self.client.get(
            url_for("api.get_user_by_id", user_id=1),
            headers=self.get_auth_basic(self.user1_credentials)
        )
        self.assertEqual(resp.status_code, 200)

        self.assertEqual(resp.json, {
            "username": self.user1_data["username"],
            "firstName": self.user1_data["firstName"],
            "lastName": self.user1_data["lastName"],
            "email": self.user1_data["email"],
            "phone": self.user1_data["phone"],
            "birthDate": self.user1_data["birthDate"],
            "isAdmin": self.user1_data["isAdmin"],
            "userStatus": ANY,
            "code": 200,
        })

    def test_get_user_by_id_not_admin(self):
        db_utils.create_entry(User, **self.user1_data_hashed)
        db_utils.create_entry(User, **self.user2_data_hashed)
        resp = self.client.get(
            url_for("api.get_user_by_id", user_id=1),
            headers=self.get_auth_basic(self.user2_credentials)
        )
        self.assertEqual(resp.status_code, 401)

        self.assertEqual(resp.json, {
            "error": ANY,
            "code": 401
        })

class TestActionUserByUsername(BaseTestCase):
    def test_get_user_by_username(self):
        db_utils.create_entry(User, **self.user1_data_hashed)
        resp = self.client.get(
            url_for("api.user_admin", user_name='user1'),
            headers=self.get_auth_basic(self.user1_credentials)
        )
        self.assertEqual(resp.status_code, 200)

        self.assertEqual(resp.json, {
            "username": self.user1_data["username"],
            "firstName": self.user1_data["firstName"],
            "lastName": self.user1_data["lastName"],
            "email": self.user1_data["email"],
            "phone": self.user1_data["phone"],
            "birthDate": self.user1_data["birthDate"],
            "isAdmin": self.user1_data["isAdmin"],
            "userStatus": ANY,
            "code": 200,
        })

    def test_get_user_by_username_doesnt_exist(self):
        db_utils.create_entry(User, **self.user1_data_hashed)
        resp = self.client.get(
            url_for("api.user_admin", user_name='user'),
            headers=self.get_auth_basic(self.user1_credentials)
        )
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json, {
            "code": 404,
            "error": "Not found"
        })

    def test_delete_user_by_username(self):
        db_utils.create_entry(User, **self.user1_data_hashed)
        resp = self.client.delete(
            url_for("api.user_admin", user_name='user1'),
            headers=self.get_auth_basic(self.user1_credentials),
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {
            "username": "0",
            "firstName": self.user1_data["firstName"],
            "lastName": self.user1_data["lastName"],
            "email": self.user1_data["email"],
            "phone": self.user1_data["phone"],
            "birthDate": self.user1_data["birthDate"],
            "isAdmin": self.user1_data["isAdmin"],
            "userStatus": 0,
            "code": 200,
        })

    def test_delete_user_by_username_doesnt_exist(self):
        db_utils.create_entry(User, **self.user1_data_hashed)
        resp = self.client.delete(
            url_for("api.user_admin", user_name='user'),
            headers=self.get_auth_basic(self.user1_credentials)
        )
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json, {
            "code": 404,
            "error": "Not found"
        })


class TestCreateClassroom(BaseTestCase):
    def test_create_classroom(self):
        db_utils.create_entry(User, **self.user1_data_hashed)
        resp = self.client.post(
            url_for("api.create_classroom"),
            json=self.classroom1_data,
            headers=self.get_auth_basic(self.user1_credentials)
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {
            "name": self.classroom1_data["name"],
            "capacity": self.classroom1_data["capacity"],
            "classroomStatus": "available",
            "code": 200
        })
        self.assertTrue(
            Session.query(Classroom).filter_by(name=self.classroom1_data["name"]).one()
        )

    def test_create_classroom_name_taken(self):
        db_utils.create_entry(User, **self.user1_data_hashed)
        db_utils.create_entry(Classroom, **self.classroom1_data)
        resp = self.client.post(
            url_for("api.create_classroom"),
            json=self.classroom1_data,
            headers=self.get_auth_basic(self.user1_credentials)
        )
        self.assertEqual(resp.status_code, 402)
        self.assertEqual(resp.json, {
            "code": 402,
            "error": "Classroom with entered name already exists"
        })


class TestGetClassroomsByStatus(BaseTestCase):
    def test_get_classrooms_by_status(self):
        db_utils.create_entry(User, **self.user1_data_hashed)
        db_utils.create_entry(Classroom, **self.classroom1_data)
        db_utils.create_entry(Classroom, **self.classroom2_data)

        resp = self.client.get(
            url_for("api.find_classroom_by_status"),
            json=self.classroom_2statuses,
            headers=self.get_auth_basic(self.user1_credentials)
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, [
            {
                "capacity": self.classroom1_data["capacity"],
                "classroomStatus": "available",
                "name": self.classroom1_data["name"]
            },
            {
                "capacity": self.classroom2_data["capacity"],
                "classroomStatus": "available",
                "name": self.classroom2_data["name"]
            },
            {
                "code": 200
            }
        ])

    def test_get_classrooms_by_status_invalid_status(self):
        db_utils.create_entry(User, **self.user1_data_hashed)
        db_utils.create_entry(Classroom, **self.classroom1_data)
        db_utils.create_entry(Classroom, **self.classroom2_data)

        resp = self.client.get(
            url_for("api.find_classroom_by_status"),
            json=self.classroom_invalid_statuses,
            headers=self.get_auth_basic(self.user1_credentials)
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json, {"error": "Invalid status value(s). "
                                              "Should be list with maximum size = 2, "
                                              "elements should be strings \'available' or 'unavailable' ",
                                     "code": 400})


class TestActionClassroom(BaseTestCase):
    def test_get_classroom_by_id(self):
        db_utils.create_entry(User, **self.user1_data_hashed)
        db_utils.create_entry(Classroom, **self.classroom1_data)

        resp = self.client.get(
            url_for("api.classroom", classroom_id=1),
            headers=self.get_auth_basic(self.user1_credentials)
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {
            "name": self.classroom1_data["name"],
            "capacity": self.classroom1_data["capacity"],
            "classroomStatus": ANY,
            "code": 200
        })

    def test_classroom_doesnt_exist(self):
        db_utils.create_entry(User, **self.user1_data_hashed)

        resp = self.client.get(
            url_for("api.classroom", classroom_id=1),
            headers=self.get_auth_basic(self.user1_credentials)
        )
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json, {
            "code": 404,
            "error": "Not found"
        })

    def test_update_classroom_by_id(self):
        db_utils.create_entry(User, **self.user1_data_hashed)
        db_utils.create_entry(Classroom, **self.classroom1_data)

        resp = self.client.put(
            url_for("api.classroom", classroom_id=1),
            json=self.classroom1_update_data,
            headers=self.get_auth_basic(self.user1_credentials)
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {
            "name": self.classroom1_update_data["name"],
            "capacity": self.classroom1_data["capacity"],
            "classroomStatus": ANY,
            "code": 200
        })

    def test_delete_classroom_by_id(self):
        db_utils.create_entry(User, **self.user1_data_hashed)
        db_utils.create_entry(Classroom, **self.classroom1_data)

        resp = self.client.delete(
            url_for("api.classroom", classroom_id=1),
            headers=self.get_auth_basic(self.user1_credentials)
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {
            "code": 200,
            "message": "deleted"
        })


class TestCreateOrder(BaseTestCase):
    def test_create_order(self):
        db_utils.create_entry(User, **self.user1_data_hashed)
        db_utils.create_entry(Classroom, **self.classroom1_data)
        resp = self.client.post(
            url_for("api.place_order"),
            json=self.order1_data,
            headers=self.get_auth_basic(self.user1_credentials)
        )
        self.assertEqual(resp.status_code, 200)
        start_time = self.order1_data["start_time"].split(' ')[0] + "T" + self.order1_data["start_time"].split(' ')[1]
        end_time = self.order1_data["end_time"].split(' ')[0] + "T" + self.order1_data["end_time"].split(' ')[1]
        self.assertEqual(resp.json, {
            "classroomId": self.order1_data["classroomId"],
            "start_time": start_time,
            "end_time": end_time,
            "orderStatus": "placed",
            "code": 200,
            "userId": 1
        })
        self.assertTrue(
            Session.query(Order).filter_by(start_time=start_time).one()
        )

    def test_create_order_classroom_not_free_in_range(self):
        db_utils.create_entry(User, **self.user1_data_hashed)
        db_utils.create_entry(Classroom, **self.classroom1_data)
        db_utils.create_order(**self.order1_data_with_userid)
        resp = self.client.post(
            url_for("api.place_order"),
            json=self.order1_data,
            headers=self.get_auth_basic(self.user1_credentials)
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json, {"error": "This classroom will be unavailable in entered period of time",
                                     "code": 400})


class TestGetOrdersByStatus(BaseTestCase):
    def test_get_classrooms_by_status(self):
        db_utils.create_entry(User, **self.user1_data_hashed)
        db_utils.create_entry(User, **self.user2_data_hashed)
        db_utils.create_entry(Classroom, **self.classroom1_data)
        db_utils.create_entry(Classroom, **self.classroom2_data)
        db_utils.create_order(**self.order1_data_with_userid)
        db_utils.create_order(**self.order2_data_with_userid)

        resp = self.client.get(
            url_for("api.get_orders_by_status"),
            json=self.order_2statuses,
            headers=self.get_auth_basic(self.user1_credentials)
        )

        self.assertEqual(resp.status_code, 200)
        start_time1 = self.order1_data["start_time"].split(' ')[0] + "T" + self.order1_data["start_time"].split(' ')[1]
        start_time2 = self.order2_data["start_time"].split(' ')[0] + "T" + self.order2_data["start_time"].split(' ')[1]

        end_time1 = self.order1_data["end_time"].split(' ')[0] + "T" + self.order1_data["end_time"].split(' ')[1]
        end_time2 = self.order2_data["end_time"].split(' ')[0] + "T" + self.order2_data["end_time"].split(' ')[1]

        self.assertEqual(resp.json, [
            {"classroomId": self.order1_data_with_userid["classroomId"],
             "start_time": start_time1,
             "end_time": end_time1,
             "orderStatus": ANY,
             "userId": self.order1_data_with_userid["userId"]
             },
            {"classroomId": self.order2_data_with_userid["classroomId"],
             "start_time": start_time2,
             "end_time": end_time2,
             "orderStatus": ANY,
             "userId": self.order2_data_with_userid["userId"]
             },
            {"code": 200}
        ])


class TestActionOrder(BaseTestCase):
    def test_get_order_by_id(self):
        db_utils.create_entry(User, **self.user1_data_hashed)
        db_utils.create_entry(Classroom, **self.classroom1_data)
        db_utils.create_order(**self.order1_data_with_userid)

        resp = self.client.get(
            url_for("api.order", order_id=1),
            headers=self.get_auth_basic(self.user1_credentials)
        )
        self.assertEqual(resp.status_code, 200)
        start_time = self.order1_data["start_time"].split(' ')[0] + "T" + self.order1_data["start_time"].split(' ')[1]
        end_time = self.order1_data["end_time"].split(' ')[0] + "T" + self.order1_data["end_time"].split(' ')[1]
        self.assertEqual(resp.json, {
            "classroomId": self.order1_data["classroomId"],
            "start_time": start_time,
            "end_time": end_time,
            "orderStatus": "placed",
            "code": 200,
            "userId": 1
        })

    def test_update_order_by_id(self):
        db_utils.create_entry(User, **self.user1_data_hashed)
        db_utils.create_entry(Classroom, **self.classroom1_data)
        db_utils.create_order(**self.order1_data_with_userid)

        resp = self.client.put(
            url_for("api.order", order_id=1),
            json={"orderStatus": "denied"},
            headers=self.get_auth_basic(self.user1_credentials)
        )

        self.assertEqual(resp.status_code, 200)
        start_time = self.order1_data["start_time"].split(' ')[0] + "T" + self.order1_data["start_time"].split(' ')[1]
        end_time = self.order1_data["end_time"].split(' ')[0] + "T" + self.order1_data["end_time"].split(' ')[1]
        self.assertEqual(resp.json, {
            "classroomId": self.order1_data["classroomId"],
            "start_time": start_time,
            "end_time": end_time,
            "orderStatus": "denied",
            "code": 200,
            "userId": 1
        })

    def test_delete_order_by_id(self):
        db_utils.create_entry(User, **self.user1_data_hashed)
        db_utils.create_entry(Classroom, **self.classroom1_data)
        db_utils.create_order(**self.order1_data_with_userid)

        resp = self.client.delete(
            url_for("api.order", order_id=1),
            headers=self.get_auth_basic(self.user1_credentials)
        )

        self.assertEqual(resp.status_code, 200)

        self.assertEqual(resp.json, {
            "code": 200,
            "message": "deleted"
        })


if __name__ == "__main__":
    unittest.main()
