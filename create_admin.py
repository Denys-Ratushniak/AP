from classroom_booking.models import Session, User
from flask_bcrypt import generate_password_hash

session = Session()

user1 = User(username="admin", firstName="admin", lastName="admin", email="admin@gmail.com",
             password=generate_password_hash("admin"), phone="+380963651527",
             birthDate="2000-01-01", isAdmin='1')

session.add(user1)
session.commit()
