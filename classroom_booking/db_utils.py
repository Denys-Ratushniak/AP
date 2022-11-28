from sqlalchemy import select
from classroom_booking.models import Session, User, Classroom, Order
from sqlalchemy.sql import exists
from datetime import datetime
from classroom_booking.schemas import ClassroomData


def create_entry(model_class, *, commit=True, **kwargs):
    session = Session()
    entry = model_class(**kwargs)
    session.add(entry)
    if commit:
        session.commit()
    return entry


def is_name_taken(model_class, name):
    session = Session()
    if model_class == User:
        return session.query(exists().where(model_class.username == name)).scalar()

    if model_class == Classroom:
        return session.query(exists().where(model_class.name == name)).scalar()


def is_id_taken(model_class, uid):
    session = Session()
    return session.query(exists().where(model_class.id == uid)).scalar()


def get_entry_by_id(model_class, uid, **kwargs):
    session = Session()
    return session.query(model_class).filter_by(id=uid, **kwargs).one()


def get_entry_by_name(model_class, user_name, **kwargs):
    session = Session()
    return session.query(model_class).filter_by(username=user_name, **kwargs).one()


def update_entry(entry, *, commit=True, **kwargs):
    session = Session()
    for key, value in kwargs.items():
        setattr(entry, key, value)
    if commit:
        session.commit()
    return entry


def delete_entry(entry, commit=True):
    session = Session()
    session.delete(entry)
    if commit:
        session.commit()
    return


def get_list_of_classrooms_by_1or2_statuses(request):
    session = Session()
    statuses = request['status']
    q1 = session.query(Classroom).filter_by(classroomStatus=statuses[0]).all()
    q2 = []
    if len(statuses) > 1:
        q2 = session.query(Classroom).filter_by(classroomStatus=statuses[1]).all()

    return q1 + q2


def get_list_of_orders_by_1or2_statuses(request):
    session = Session()
    statuses = request['status']
    q1 = session.query(Order).filter_by(orderStatus=statuses[0]).all()
    q2 = []
    if len(statuses) > 1:
        q2 = session.query(Order).filter_by(orderStatus=statuses[1]).all()

    return q1 + q2


def find_orders_by_userid(userid):
    session = Session()
    return session.query(Order).filter_by(userId=userid).all()


def reload_classroom_statuses(commit=True):
    session = Session()
    current_time = datetime.now()

    for classroom_id in Session.scalars(select(Classroom.id)).all():

        classroom = get_entry_by_id(Classroom, classroom_id)

        if session.query(exists().where(Order.classroomId == classroom_id,
                                        Order.orderStatus == 'placed',
                                        Order.start_time <= current_time,
                                        current_time <= Order.end_time,
                                        )).scalar():

            change = {"classroomStatus": "unavailable"}
        else:
            change = {"classroomStatus": "available"}

        classroom_data = ClassroomData().load(change)
        update_entry(classroom, **classroom_data)

    if commit:
        session.commit()
    return


def create_order(commit=True, **orderinfo):
    session = Session()

    userid = orderinfo.get('userId')
    classroomid = orderinfo.get('classroomId')

    user = get_entry_by_id(User, userid)
    classroom = get_entry_by_id(Classroom, classroomid)

    order = Order(**orderinfo, user=user, classroom=classroom)

    session.add(order)
    if commit:
        session.commit()
    return order


def is_classroom_free_in_range(classroomid, start_time, end_time):
    session = Session()

    if session.query(exists().where(Order.classroomId == classroomid,
                                    Order.orderStatus == 'placed',
                                    Order.start_time <= start_time,
                                    start_time < Order.end_time
                                    )).scalar():
        return False

    if session.query(exists().where(Order.classroomId == classroomid,
                                    Order.orderStatus == 'placed',
                                    Order.start_time < end_time,
                                    end_time <= Order.end_time
                                    )).scalar():
        return False

    if session.query(exists().where(Order.classroomId == classroomid,
                                    Order.orderStatus == 'placed',
                                    start_time <= Order.start_time,
                                    Order.start_time < end_time
                                    )).scalar():
        return False

    if session.query(exists().where(Order.classroomId == classroomid,
                                    Order.orderStatus == 'placed',
                                    start_time < Order.end_time,
                                    Order.end_time <= end_time
                                    )).scalar():
        return False

    return True
