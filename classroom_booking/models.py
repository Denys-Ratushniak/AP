from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, DateTime, SmallInteger

DB_URL = "mysql://root:E100_amx1390_maus@localhost:3306/ap"

engine = create_engine(DB_URL)
SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)
BaseModel = declarative_base()


class User(BaseModel):
	__tablename__ = "user"
	id = Column(Integer, primary_key=True)
	username = Column(String(128))
	firstName = Column(String(32))
	lastName = Column(String(32))
	email = Column(String(128))
	password = Column(String(128))
	phone = Column(String(32))
	birthDate = Column(Date)
	userStatus = Column(Enum('0', '1'), default='1')
	isAdmin = Column(Enum('0', '1'), default='0')


class Classroom(BaseModel):
	__tablename__ = "classroom"
	id = Column(Integer, primary_key=True)
	name = Column(String(32))
	classroomStatus = Column(Enum('available', 'unavailable'), default='available')
	capacity = Column(SmallInteger)


class Order(BaseModel):
	__tablename__ = "order"
	id = Column(Integer, primary_key=True)
	classroomId = Column(Integer, ForeignKey("classroom.id"))
	userId = Column(Integer, ForeignKey("user.id"))
	classroom = relationship(Classroom, foreign_keys=[classroomId], backref='classroom', lazy="joined")
	user = relationship(User, foreign_keys=[userId], backref='user', lazy="joined")
	start_time = Column(DateTime)
	end_time = Column(DateTime)
	orderStatus = Column(Enum('placed', 'denied'), default='placed')
