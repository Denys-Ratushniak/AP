from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, DateTime

DB_URL = "mysql://root:E100_amx1390_maus@localhost:3306/ap"
# DB_URL = "mysql://root:$ygnivkA12@localhost:3306/ap"
engine = create_engine(DB_URL)
SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)

BaseModel = declarative_base()


class User(BaseModel):
	__tablename__ = "user"
	id = Column(Integer, primary_key=True)
	username = Column(String)
	firstName = Column(String)
	lastName = Column(String)
	email = Column(String)
	password = Column(String)
	phone = Column(String)
	birthDate = Column(Date)
	userStatus = Column(Enum('0', '1'), default='1')


class Classroom(BaseModel):
	__tablename__ = "classroom"
	id = Column(Integer, primary_key=True)
	name = Column(String)
	classroomStatus = Column(Enum('available', 'pending', 'unavailable'), default='available')
	capacity = Column(Integer)


class Order(BaseModel):
	__tablename__ = "order_table"
	id = Column(Integer, primary_key=True)
	classroomId = Column(Integer, ForeignKey("classroom.id"))
	userId = Column(Integer, ForeignKey("user.id"))

	classroom = relationship(Classroom, foreign_keys=[classroomId], backref='classroom', lazy="joined")
	user = relationship(User, foreign_keys=[userId], backref='user', lazy="joined")

	start_time = Column(DateTime)
	end_time = Column(DateTime)
	orderStatus = Column(Enum('placed', 'denied'), default='placed')
