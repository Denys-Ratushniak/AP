
from models import Session, User, Classroom, Order

session = Session()

user1 = User(username='bohdandr', firstName='bohdan',
			 lastName='andriiv', email='bohdandr12@gmail.com',
			 password='qwerty', phone='+380960000000', birthDate="2004-10-10")

user2 = User(username='bohdandr2', firstName='bohdan2',
			 lastName='andriiv2', email='bohdandr122@gmail.com',
			 password='qwerty2', phone='+380960000002', birthDate="2003-10-10")

classroom1 = Classroom(name='classroom num1', capacity=120)
classroom2 = Classroom(name='classroom num2', capacity=90)
classroom3 = Classroom(name='classroom num3', capacity=60)

session.add(user1)
session.add(user2)

session.add(classroom1)
session.add(classroom2)
session.add(classroom3)

order1 = Order(classroom=classroom1, user=user1)
order2 = Order(classroom=classroom2, user=user2)

session.add(order1)
session.add(order2)

session.commit()
